package test;

public class Client {
	
	public static void main(String[] args) {
	RPC_Client client = new RPC_Client<>(IHello.class,"localhost","6000");
	IHello hello = (IHello)client.getClientIntance();
	System.out.println(hello.sayHello("It is Client"));
	}
}
