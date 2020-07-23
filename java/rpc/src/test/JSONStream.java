package test;

public class JSONStream {
	private String s_name;
	private String m_name;
	private Class[] a_type;
	private Object[] args;
	
	public JSONStream(String s_name,String m_name,Class[] a_type,Object[] args) {
		this.s_name = s_name;
		this.m_name = m_name;
		this.a_type = a_type;
		this.args = args;
	}

	public String getS_name() {
		return s_name;
	}

	public String getM_name() {
		return m_name;
	}

	public Class[] getA_type() {
		return a_type;
	}

	public Object[] getArgs() {
		return args;
	}
}
