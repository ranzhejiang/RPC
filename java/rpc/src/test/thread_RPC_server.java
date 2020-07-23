package test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class thread_RPC_server {
	private ServerSocket serverSocket;
	private int port;
	
	public thread_RPC_server(int port) throws IOException{
		this.port = port;
		serverSocket = new ServerSocket(this.port);
	}
	
	public void work() {
		ThreadPoolExecutor threadpool = new ThreadPoolExecutor(5,10,200,TimeUnit.SECONDS,new ArrayBlockingQueue<Runnable>(10));
		while(true) {
			try {
				Socket socket = serverSocket.accept();
				threadserver server = new threadserver(socket);
				server.register(IHello.class, HelloService.class);
				threadpool.execute(server);
			}
			catch(IOException e) {
				System.out.println(e);
			}
		}
	}
}
