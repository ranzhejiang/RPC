package test;

import com.alibaba.fastjson.JSON;

import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;

import org.dom4j.*;
import org.dom4j.io.OutputFormat;
import org.dom4j.io.XMLWriter;

public class test {
	public static void main(String[] args) {
		IHello hello = new HelloService();
		Document doc = DocumentHelper.createDocument();
		doc.addComment("this is me");
		Element root = doc.addElement("students");
		Element stuEle = root.addElement("student");
		//stuEle.addAttribute("id", hello);
		Element nameEle = stuEle.addElement("name");
		nameEle.setText("zhangsan");
		OutputFormat format = OutputFormat.createPrettyPrint();
		format.setEncoding("utf-8");
		Writer out;
		try {
			out = new FileWriter("./test.xml");
			XMLWriter writer = new XMLWriter(out,format);
			writer.write(doc);
			writer.close();
			
		}catch(IOException e) {
			
		}
	}
}
