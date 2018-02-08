"""
    简单的说明一下代码:
    IBurpExtender 这个接口是必须要导入的，我们写了一个自己的类并继承自它。
    registerExtenderCallbacks 函数也是必备的，其定义了我们在导入插件时需要做的事情，很多时候一般是初始化。
    Java Swing中的一个方法来弹出MessageBox，正常的情况如果使用Python的函数如print则会显示在插件导入时的Output栏中。
"""
from burp import IBurpExtender
from javax.swing import JOptionPane


class BurpExtender(IBurpExtender):
    def registerExtenderCallbacks(self, callbacks):
        JOptionPane.showMessageDialog(None,"Hello World zhangboss","BurpSuite Extender by DarkRay", JOptionPane.INFORMATION_MESSAGE)
        return