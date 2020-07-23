package test;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectOutputStream;
import java.io.OutputStreamWriter;
import java.lang.reflect.Method;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;

import com.alibaba.fastjson.JSONObject;
import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.io.xml.Dom4JDriver;

public class threadserver implements Runnable{
	private Socket socket;
	private Map<String,Class> serviceRegistry = new HashMap<>();

	
	public threadserver(Socket socket) {
		super();
		this.socket = socket;
	
	}
	
	@Override
	public void run() {
		InputStreamReader reader = null;
		OutputStreamWriter output = null;
		BufferedReader input = null;
		try {
			reader = new InputStreamReader(socket.getInputStream());
			input = new BufferedReader(reader); 
			
			//json
			String str = input.readLine();
			str = str.replace("string", "java.lang.String");
			JSONStream js = JSONObject.parseObject(str,JSONStream.class);
			
			//xml
//			String line = null;
//			String str = input.readLine();
//			while((line = input.readLine()) != null){
//				str = str + "\n" + line;
//				if(line.equals("</RPCCall>")) {
//					break;
//				}
//			}
//			XStream xstream = new XStream(new Dom4JDriver());
//			xstream.alias("RPCCall", JSONStream.class);
//			JSONStream js = (JSONStream)xstream.fromXML(str);
			
			System.out.println(str);
			String serviceName = js.getS_name();
			String methodName = js.getM_name();
			Class<?>[] parameterTypes = js.getA_type();
			Object[] arguments = js.getArgs();
			
			Class<?> serviceClass = serviceRegistry.get(serviceName);
			Method method = serviceClass.getMethod(methodName, parameterTypes);
			Object result = method.invoke(serviceClass.getDeclaredConstructor().newInstance(), arguments);
			
			String res = result.toString();
			JSONObject json = new JSONObject();
			json.put("res", res);
			output = new OutputStreamWriter(socket.getOutputStream());
			BufferedWriter writer = new BufferedWriter(output);
			writer.write(json.toJSONString());
			writer.flush();			
			writer.close();
			output.close();
			input.close();
			socket.close();
			
		}
		catch(Exception e) {
			e.printStackTrace();
			System.out.println(e);
		}
		
	}
	public void register(Class serviceInterface, Class impl) {	
		serviceRegistry.put(serviceInterface.getName(), impl);
		
	}
	
}
