package test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Method;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;

import com.alibaba.fastjson.JSONObject;
import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.io.xml.Dom4JDriver;

public class RPC_Server {
	
	private static final HashMap<String, Class<?>> serviceRegistry = new HashMap<>();
	private int port;
	
	public RPC_Server(int port) {
		this.port = port;
	}
	
	public RPC_Server register(Class serviceInterface, Class impl) {
		
		serviceRegistry.put(serviceInterface.getName(), impl);
		return this;
	}
	
	public void run() throws IOException{
		
		ServerSocket server = new ServerSocket();
		server.bind(new InetSocketAddress(port));
		InputStreamReader reader = null;
		ObjectOutputStream output = null;
		Socket socket = null;
		BufferedReader input = null;
		
		try {
			while(true) {
			socket = server.accept();
			reader = new InputStreamReader(socket.getInputStream());
			input = new BufferedReader(reader); 
			
			
			String str = input.readLine();
			System.out.println("I get it");
			System.out.println(str);
			
			//json
			//JSONStream js = JSONObject.parseObject(jsonstr,JSONStream.class);
			
			//xml
			XStream xstream = new XStream(new Dom4JDriver());
			JSONStream js = (JSONStream)xstream.fromXML(str);
			System.out.println(js.getS_name());
			String serviceName = js.getS_name();
			String methodName = js.getM_name();
			Class<?>[] parameterTypes = js.getA_type();
			Object[] arguments = js.getArgs();
			Class<?> serviceClass = serviceRegistry.get(serviceName);
			
			Method method = serviceClass.getMethod(methodName, parameterTypes);
			Object result = method.invoke(serviceClass.getDeclaredConstructor().newInstance(), arguments);
			
			output = new ObjectOutputStream(socket.getOutputStream());
			output.writeObject(result);
			}
		}
		catch(Exception e) {
			e.printStackTrace();
			System.out.println(e);
		}
		finally {
			output.close();
			input.close();
			socket.close();
		}
	}
}
