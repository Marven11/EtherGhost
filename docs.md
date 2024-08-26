# 如何自定义Encoder

首先根据启动时打印的路径打开游魂的配置文件夹，找到其中的`modules/php_encoders`文件夹

新建python文件（如`example.py`）并往其中写入以下内容：

```python
import base64

def encode(code: str):
    return f"eval(base64_decode({base64.b64encode(code.encode()).decode()!r}));"
```

最后重启游魂即可在webshell编辑页面看到encoder

注意：encode函数的返回值可以是str或bytes，代表需要执行的PHP代码

# 如何自定义Decoder

首先根据启动时打印的路径打开游魂的配置文件夹，找到其中的`modules/php_decoders`文件夹

新建python文件（如`example.py`）并往其中写入以下内容：

```python
import base64

phpcode = """
function decoder_echo_raw($s) {
    echo base64_encode($s);
}
"""

def decode(s: str) -> str:
    return base64.b64decode(s).decode()
```

最后重启游魂即可在webshell编辑页面看到decoder

# 如何将蚁剑的encoder和decoder导入到游魂中

首先根据启动时打印的路径打开游魂的配置文件夹

然后在`AntSwordEncoder`或`AntSwordDecoder`中写入js文件，并重启游魂即可

比如在`AntSwordEncoder`写入文件`example-base64.js`

```js
module.exports = (pwd, data, ext={}) => {
    let randomID = `_0x${Math.random().toString(16).substr(2)}`;
    data[randomID] = Buffer.from(data['_']).toString('base64');
    data[pwd] = `eval(base64_decode($_POST[${randomID}]));`;
    delete data['_'];
    return data;
}
```

或者在`AntSwordDecoder`写入文件`example-base64.js`

```js
module.exports = {
  asoutput: () => {
    return `function asenc($out){
      return @base64_encode($out);
    }
    `.replace(/\n\s+/g, '');
  },
  decode_buff: (data, ext={}) => {
    return Buffer.from(data.toString(), 'base64');
  }
}
```

完成后可以在webshell编辑界面看到encoder

注意：游魂不支持和蚁剑内部设计高度相关的某些环境变量，某些encoder需要进行修改才能使用

# 如何自定义壁纸

把壁纸重命名为`bg.jpg`, `bg.png`或者`bg.webp`丢到游魂的配置文件夹（启动时打印的路径），然后在游魂的设置页面把主题改成“玻璃”

# Q&A: 为什么不支持在网页端添加encoder和decoder?

Encoder和Decoder会在服务端启动的时候作为代码被加载，如果蓝队登陆了红队的游魂则可以通过添加Encoder的方式控制服务器

所以为了防止RCE漏洞，游魂不应该支持在网页端添加encoder和decoder

# Q&A: 为什么正向代理有Vessel和伪正向两种代理？Vessel是什么？

Vessel是我自己写的一个PHP持久化内存马，可以通过文件和Session两种方式通信。本来正向代理功能是打算直接联动[Neo-reGeorg](https://github.com/L-codes/Neo-reGeorg)的，但是Neo-reGeorg的许可证是GPL3，如果用他们的代码的话就要换许可证了。

本来计划是写一个PHP内存马然后通过文件实现与内存马的通信，但是看了Neo-reGeorg的代码后才发现Session竟然可以这么用来通信，然后才加上了Session的通信方式。

Vessel没有经过多少测试，功能也只是基本能用的状态，速度应该也比不上Neo-reGeorg，但是用来做内网渗透应该是够的。

伪正向代理是用gopher协议以类似SSRF的方式发送流量，因为是SSRF所以基本上只能支持HTTP之类的协议。
