package test;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.net.InetSocketAddress;
import java.net.Socket;

import org.dom4j.io.*; 
import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.io.xml.Dom4JDriver;

import com.alibaba.fastjson.*;

public class RPC_Client<T> implements InvocationHandler{
	
	private Class<T> serviceInterface;
	private InetSocketAddress addr;
	
	public RPC_Client(Class<T> serviceInterface,String ip,String port) {
		
		this.serviceInterface = serviceInterface;
		this.addr = new InetSocketAddress(ip,Integer.parseInt(port));
		
	}
	
	public T getClientIntance() {
		return (T)Proxy.newProxyInstance(serviceInterface.getClassLoader(), new Class<?>[] {serviceInterface}, this);
	}
	
	@Override
	public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
		
		Socket socket = null;
		OutputStreamWriter writer = null;
		BufferedWriter output = null;
		InputStreamReader input = null;
		
		try {
			socket = new Socket();
			socket.connect(addr);
			JSONStream js = new JSONStream(serviceInterface.getName(),method.getName(),method.getParameterTypes(),args);
			
			//json 
			
			
			String jsonstr = JSON.toJSONString(js);
			String out = jsonstr+"\n";
			System.out.print(out);
			
			//xml
//			XStream xstream = new XStream(new Dom4JDriver());
//			xstream.alias("RPCCall", JSONStream.class);
//			String out = xstream.toXML(js) + "\n";
			
			writer = new OutputStreamWriter(socket.getOutputStream());
			output = new BufferedWriter(writer);
			
			output.write(out);
			output.flush();
			input = new InputStreamReader(socket.getInputStream());
			BufferedReader reader = new BufferedReader(input); 
			String res = reader.readLine();
			//System.out.print(res);
			String json = JSONObject.parseObject(res,String.class);
 			return json;
			
			
			
		}
		
		finally {
			
			socket.close();
			output.close();
			input.close();
			
		}
		
	}

}
