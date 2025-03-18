This is the example project referred to in the Struts 2 documentation, [How To Create A Struts 2 Web Application](http://struts.apache.org/getting-started/how-to-create-a-struts2-web-application.html) tutorial.

## Building the war
### Using Maven
To build the application's war file run `mvn clean package` from the project's root folder.

The war file is created in the `target` sub-folder.

## Running the application
### Using Maven
run the command `mvn jetty:run`

### Using a Servlet container
Copy the war file to your Servlet container (e.g. Tomcat) and then startup the Servlet container.

## Accessing the application

In a web browser go to:  [http://localhost:8080/basic-struts/index.action](http://localhost:8080/basic-struts/index.action) 

You should see a web page with 

```
Welcome to Struts 2!
```
