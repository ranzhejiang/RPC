package test;

public class HelloService implements IHello{

	@Override
	public String sayHello(String str) {
		
		return "server:" + str;
		
	}
	
	
	
}
