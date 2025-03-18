This is the example project referred to in the
Struts 2 documentation, Ready, Set, Go tutorial.
See:  http://struts.apache.org.

To build the application's war file run mvn clean package
from the project's root folder.

The war file is created in the target sub-folder.

Copy the war file to your Servlet container (e.g. Tomcat) and 
then startup the Servlet container.

Or if you are using maven you can run command:
mvn jetty:run


In a web browser go to:  http://localhost:8080/basic-struts/index.action.

You should see a web page with Welcome to Struts 2!

