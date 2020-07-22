package test;

import java.io.IOException;

public class server {
	
	public static void main(String[] args) throws IOException {
//		RPC_Server server = new RPC_Server(6000);
//		RPC_Server worker = server.register(IHello.class, HelloService.class);
//		worker.run();
		new Thread( () ->  {
	        try {
	            thread_RPC_server server = new thread_RPC_server(6000);
	            server.work();
	        } catch (IOException e){
	            System.out.println(e.getMessage());
	        }
	    } ).start();
	
	}
}
