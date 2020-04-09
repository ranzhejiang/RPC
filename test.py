
import collections
import itertools

Instruction = collections.namedtuple('Instruction', ('opcode','write_register', 'read_registers'))
"""
 Instruction(opcode='ADD.D', write_register='F2', read_registers=('F0', 'F4'))
"""

class _InstructionTracker:
  
  class _Instruction:
    _new_state = None
    state = 'unissued'
    states = set(('unissued', 'IS', 'reservation-station', 'queued-for-EX','EX', 'queued-for-WB', 'WB', 'waiting-for-commit', 'CM'))
    dependence_count = 0

    def __init__(self, instruction, index):
      self.opcode = instruction.opcode
      self.write_register = instruction.write_register
      self.read_registers = instruction.read_registers
      self.index = index
      self.history = list()
      self.messages = set()

    def issue(self):
      self._set_state('IS')

    def wait_in_reservation_station(self):
      self._set_state('reservation-station')

    def enqueue_for_execute(self):
      self._set_state('queued-for-EX')

    def execute(self):
      self._set_state('EX')

    def enqueue_for_writeback(self):
      self._set_state('queued-for-WB')

    def writeback(self):
      self._set_state('WB')

    def wait_for_commit(self):
      self._set_state('waiting-for-commit')

    def commit(self):
      self._set_state('CM')

    def ready_to_commit(self):
      return self.state in ('WB', 'waiting-for-commit')

    def _set_state(self, state):
      if state not in self.states:
        raise Exception("Tried to set illegal state {0}".format(state))
      self._new_state = state

    def update(self, new_cycle):
      if self. _new_state:
        if self._new_state in set(('IS', 'EX', 'WB', 'CM')):
          self.history.append((self._new_state, new_cycle))
        if self.state == 'EX':
          self.history.append(('EX-end', new_cycle - 1))
        self.state = self._new_state
        self._new_state = None

    def __repr__(self):
      return str(self)

    def __str__(self):
      return ('{0.index}: {0.opcode} {0.write_register} {0.read_registers} state: '
          '{0.state} pending state: {0._new_state} d_c: '
          '{0.dependence_count}'.format(self))

    def final_dict(self):
      def format_msg(msg):
        return '{0} on {1} (from {2})'.format(*msg)

      def get_cycle(state):
        index = list(map(lambda x: x[0], self.history)).index(state)
        if state == 'EX':
          start_cycle = str(self.history[index][1])
          end_cycle = get_cycle('EX-end')
          if start_cycle != end_cycle:
            return '{0!s}-{1}'.format(str(int(self.history[index][1])+1), str(int(end_cycle)+1))
          else:
            return str(int(start_cycle)+1)
        else:
          return str(self.history[index][1])

      reg_iter = itertools.chain((self.write_register,), self.read_registers)
      instruction_text = '{0} {1}'.format(self.opcode, ', '.join(reg_iter))
      # print('**************')
      # print(str(int(get_cycle('WB'))+1))
      return {'index': self.index, 'instruction': instruction_text,'IS': get_cycle('IS'), 'EX': get_cycle('EX'),'WB': str(int(get_cycle('WB'))+1), 'CM': str(int(get_cycle('CM'))+1),'messages': '; '.join(format_msg(m) for m in self.messages)}

  def __init__(self, instructions):
    self.instructions = [_InstructionTracker._Instruction(instr, i) for
                         i, instr in enumerate(instructions)]

  def issue_next(self, reorder_buffer):
    unissued = filter(lambda i: i.state == "unissued", self.instructions)
    unissued = list(unissued)
    if unissued and not reorder_buffer.is_full():
      reorder_buffer.add(unissued[0])
      unissued[0].issue()

  def update(self, new_cycle):
    for instruction in self.instructions:
      instruction.update(new_cycle)
    if self.instructions[-1].state == 'CM':
      return True
    if new_cycle > 1000:
      print ("failed to stop")
      return True

class _ReorderBuffer:
  def __init__(self, length=1e6):
    self.storage = list()
    self.length = length  # Default arg is basically infinity

  def add(self, instruction):
    if self.is_full():
      raise Exception("Reorder buffer just got too full!! Oops!")
    self.storage.append(instruction)

  def is_full(self):
    return len(self.storage) >= self.length

  def commit(self):
    if len(self.storage) == 0:
      return
    head = self.storage[0]
    if head.ready_to_commit():
      head.commit()
      self.storage.pop(0)

  def IS_instruction_iterator(self, instruction_tracker):
    return filter(lambda i: i.state == "IS", self.storage)

class _FunctionalUnits:
  class FunctionalUnit:
    current_instruction = None
    end_cycle = None

    def __init__(self, duration, name):
      self.duration = duration
      self.name = name
      self.queue = list()

    def __repr__(self):
      return str(self)

    def __str__(self):
      return ('{0.name}: {0.current_instruction} ends at {0.end_cycle} -- ''duration {0.duration} queuelen {1}'.format(self, len(self.queue)))

    def busy(self, cycle):
      return self.end_cycle and cycle < self.end_cycle

    def _do_enqueue(self, current_cycle):
      if self.queue:
        self.queue.sort(key=lambda i: i.index)
        self.current_instruction = self.queue.pop(0)
        self.current_instruction.execute()
        self.end_cycle = current_cycle + self.duration

    def update(self, instruction_tracker, cdb, current_cycle):
      if current_cycle == self.end_cycle:
        self.current_instruction.enqueue_for_writeback()
        cdb.append(self.current_instruction)
      if not self.busy(current_cycle):
        self._do_enqueue(current_cycle)
      for instruction in self.queue:
        instruction.messages.add(('SD', self.name, self.current_instruction.index))

    def enqueue(self, instruction):
      self.queue.append(instruction)
      instruction.enqueue_for_execute()

  def __init__(self):
    int_fu = _FunctionalUnits.FunctionalUnit(1, 'Int FU')
    fp_add_fu = _FunctionalUnits.FunctionalUnit(2, 'FP Add FU')
    fp_mul_fu = _FunctionalUnits.FunctionalUnit(10, 'FP Mul FU')
    fp_div_fu = _FunctionalUnits.FunctionalUnit(40, 'FP Div FU')
    self.opcode_map = collections.defaultdict(lambda: int_fu)
    self.opcode_map.update({'ADD.D': fp_add_fu, 'SUB.D': fp_add_fu,'MUL.D': fp_mul_fu,'DIV.D': fp_div_fu})
    self.fu_list = [int_fu, fp_add_fu, fp_mul_fu, fp_div_fu]

  def enqueue(self, instruction):
    self.opcode_map[instruction.opcode].enqueue(instruction)

  def update(self, instruction_tracker, cdb, current_cycle):
    for fu in self.fu_list:
      fu.update(instruction_tracker, cdb, current_cycle)

  def __repr__(self):
    return str(self)

  def __str__(self):
    return '\n'.join(str(fu) for fu in self.fu_list)


def run(input_instructions):
  cycle = 0
  instruction_tracker = _InstructionTracker(input_instructions)
  reorder_buffer = _ReorderBuffer()
  functional_units = _FunctionalUnits()

  register_file = collections.defaultdict(lambda: None)
  reservation_station = collections.defaultdict(list)

  cdb = list()

  while not instruction_tracker.update(cycle):
    # Set up next instruction to issue next time
    instruction_tracker.issue_next(reorder_buffer)

    # Deal with instructions currently in issue stage
    for instruction in reorder_buffer.IS_instruction_iterator(instruction_tracker):
      has_dependence = False
      for register in instruction.read_registers:
        if register_file[register] is not None:
          has_dependence = True
          instruction.wait_in_reservation_station()
          instruction.dependence_count += 1
          reservation_station[register_file[register]].append(instruction.index)
          instruction.messages.add(('RAW', register, register_file[register]))
      if not has_dependence:
        functional_units.enqueue(instruction)
      register_file[instruction.write_register] = instruction.index

    # Deal with EX stage
    functional_units.update(instruction_tracker, cdb, cycle)

    # Deal with WB stage
    if cdb:
      cdb.sort(key=lambda x: x.index)
      for instruction in cdb[1:]:
        instruction.messages.add(('SD', 'CDB', cdb[0].index))
      instruction = cdb.pop(0)
      instruction.writeback()
      waiting_instructions = [instruction_tracker.instructions[i] for i in
                              reservation_station[instruction.index]]
      for instr in waiting_instructions:
        instr.dependence_count -= 1
        if instr.dependence_count == 0:
          functional_units.enqueue(instr)
      del reservation_station[instruction.index] 
      if register_file[instruction.write_register] == instruction.index:
        del register_file[instruction.write_register]

    # Deal with CM stage
    cycle += 1
    for instruction in reorder_buffer.storage:
       print (cycle,instruction)
    reorder_buffer.commit()
    
  for instruction in reorder_buffer.storage:
    print (instruction)
  print("reservation_station_state",['{0!s}: {1}'.format(k, ', '.join(map(lambda x: str(x), v))) for k, v in reservation_station.items() if v])
  print("reg_file_state:", ['{0}: {1!s}'.format(k, v) for k, v in register_file.items() if v is not None])
  print (functional_units)

# Print final state:
  format_str = '{index: >2} {instruction: >19}{IS: >5}{EX: >9}{WB: >5}{CM: >5}  {messages}'
  print (format_str.format(index='', instruction='Instruction', IS='IS',
      EX='EX', WB='WB', CM='CM', messages='Messages'))
  print (80 * '-')
  for instruction in instruction_tracker.instructions:
    print (format_str.format(**instruction.final_dict()))


# instructions = [Instruction('L.D', 'F0', ('10000',)),
#                 Instruction('ADD.D', 'F2', ('F0', 'F4')),
#                 Instruction('MUL.D', 'F4', ('F2', 'F6')),
#                 Instruction('ADD.D', 'F6', ('F8', 'F10')),
#                 Instruction('DADDI', 'R1', ('R1',)),
#                 Instruction('L.D', 'F1', ('R2',)),
#                 Instruction('DIV.D', 'F1', ('F2','F6')),
#                 Instruction('MUL.D', 'F1', ('F1', 'F8')),
#                 Instruction('ADD.D', 'F6', ('F3', 'F5')),
#                 Instruction('DADDI', 'R2', ('R2',)),
#                 Instruction('DADDI', 'R3', ('R3',)),
#                 Instruction('DADDI', 'R4', ('R4',)),
#                 Instruction('DADDI', 'R5', ('R5',))]
instructions = [Instruction('L.D', 'F6', ('10000',)),
                Instruction('L.D', 'F2', ('10000',)),
                Instruction('MUL.D', 'F0', ('F2','F4')),
                Instruction('SUB.D', 'F8', ('F2','F6')),
                Instruction('DIV.D', 'F0', ('F0','F6')),
                Instruction('ADD.D', 'F6', ('F8','F2'))]

run(instructions)
