---
layout: post
category: 技术
tags: https android
title: Android https通信
date: 2016-02-24T10:39:14+08:00
---

** HTTPS
*HTTPS*（也被称为 *HTTP over TLS*, *HTTP over SSL*, *HTTP Secure*)。

从字面上我们可以理解HTTPS为：使用SSL/TLS的HTTP，从而实现Secure通信。

首先我们明白一点TLS为SSL的后续版本。TLS1.0也被称为SSL3.1。

* 1995 SSL2.0
* 1996 SSL3.0
* 1999 TLS1.0 （也被称为SSL3.1)
* 2006 TLS1.1 （也被称为SSL3.2)
* 2008 TLS1.2 （也被称为SSL3.3)
* 2011 TLS1.2修订版

** Android Https 例子
我们暂且不去讨论SSL为何物，先只看看在Android中怎么实现https通信。

项目地址:<https://github.com/huhuang03/HttpsAndroid>

**# 普通http通信
普通http通信我们很熟悉。就是发送一个http请求，Android提供了一个UrlConnection和一个HttpClient。

这里为了简便我们使用RxJava风格的api。例子是通过ip定位的api获取ip和位置信息，数据为json格式，我们用LocData接收它。


    String url = "http://freegeoip.net/json/";
    Thyi.request(context, Thyi.GET, url, null, LocData.class)
          .subscribe(new Subscriber<LocData>() {
              @Override
              public void onCompleted() {
                  Log.i(TAG, "onCompleted: ");
              }

              @Override
              public void onError(Throwable e) {
                  Log.i(TAG, "onError: ");
              }

              @Override
              public void onNext(LocData locData) {
                  Log.i(TAG, "onNext(): " + locData);
              }
          });

实际运行例子，可以正确打印出LocData的信息。

**# https通信
我们知道SSL通信对信息进行了加密。我们*暂时*这样理解，在SSL协议中，服务端配置了一个私钥和对应的公钥，客户端拿到公钥对信息进行加密。
服务端通过私钥进行解密。

我们拿到一个公钥，如何保证公钥的正确性呢？因为如果公钥被篡改了客户端还不知道，则其他人就可以冒充服务器对我们的数据进行解密了。

这就需要用到证书了，证书中包含了公钥，证书使用了服务器的私钥进行签名。如果证书是可信赖的，则公钥就是可信赖的。

但是我们怎么知道证书是可信赖的呢，一般客户端的做法是预存了一些可信赖的证书列表，如果服务端给的证书在其中，则证明证书是可信赖的。

但是证书是任何人都可以颁布的，客户端不能做到去预存每一个可信赖的证书，解决这个问题的办法就是全球可信赖的证书颁发机构（Centificate Authorities（CA）），由CA去给合法服务端
颁发证书，而客户端只要预存这些可信赖的CA，比如从Android4.2开始，Android就预存了100多个CA。

所以客户端https通信就分成了两个。一是证书是知名CA颁发，一是证书由自己颁发（也可能是一些封闭机构，如政府，教育结构颁发）。

**** 证书由CA颁发
对于CA颁发的证书，因为Android已经预存了CA的证书，所以不需要任何额外的工作。只是将url http改为https。

下面这个例子是去拿wikipedia.org的首页数据，使用chrome客户端。我们可以查看到wikipedia.org的证书由GlobalSign Organization Validation CA颁发，而GlobalSign Origanization Validataion CA的证书已经由Android系统预存。
所以widipedia.org的证书是可信赖的。

![](/images/wikipedia_crt.png)

不需要任何额外工作：

    Thyi.request(context, "https://wikipedia.org")
        .subscribe(new Subscriber<String>() {
            @Override
            public void onCompleted() {
                Log.i(TAG, "onCompleted: ");
            }

            @Override
            public void onError(Throwable e) {
                Log.i(TAG, "onError: ");
            }

            @Override
            public void onNext(String s) {
                Log.i(TAG, "onNext: " + s);
            }
        });

验证一下，可以正确获取到数据。

**** 证书由自己颁发
对于证书由自己颁发的服务器，我们按照普通的方式发送请求，可以看到会报一个找不到可信赖证书的异常。
我们拿12306的网站来看，通过查看，我们可以看到12306的证书是自己颁给自己的。


	Thyi.request(context, "https://kyfw.12306.cn/otn")
	.subscribe(new Subscriber<String>() {
		@Override
		public void onCompleted() {
			Log.i(TAG, "onCompleted: ");
		}

		@Override
		public void onError(Throwable e) {
			Log.i(TAG, "onError: ");
			e.printStackTrace();
		}

		@Override
		public void onNext(String s) {
			Log.i(TAG, "onNext: ");
		}
	});

会报证书不可信的错误

	javax.net.ssl.SSLHandshakeException: java.security.cert.CertPathValidatorException: Trust anchor for certification path not found.
		at org.apache.harmony.xnet.provider.jsse.OpenSSLSocketImpl.startHandshake(OpenSSLSocketImpl.java:374)
		at libcore.net.http.HttpConnection.setupSecureSocket(HttpConnection.java:209)
		at libcore.net.http.HttpsURLConnectionImpl$HttpsEngine.makeSslConnection(HttpsURLConnectionImpl.java:478)
		at libcore.net.http.HttpsURLConnectionImpl$HttpsEngine.connect(HttpsURLConnectionImpl.java:433)
		at libcore.net.http.HttpEngine.sendSocketRequest(HttpEngine.java:290)
		at libcore.net.http.HttpEngine.sendRequest(HttpEngine.java:240)
		at libcore.net.http.HttpURLConnectionImpl.getResponse(HttpURLConnectionImpl.java:282)
		at libcore.net.http.HttpURLConnectionImpl.getInputStream(HttpURLConnectionImpl.java:177)
		at libcore.net.http.HttpsURLConnectionImpl.getInputStream(HttpsURLConnectionImpl.java:271)

对待这种情况，我们可以把证书预存下来，给URLConnection。过程有点曲折，要通过证书生成一个KeyStore，通过KeyStore创建一个TrustManager。将TrustManager传递给HtppsConnection。这个HttpsConnection就可以正常使用SSL通信了。

     //load证书，证书放在了assert目录中
     InputStream caInput = null;
     Certificate ca = null;
     try {
         caInput = new BufferedInputStream(getAssets().open("kyfw.12306.cn.cer"));
         CertificateFactory cf = CertificateFactory.getInstance("X.509");
         ca = cf.generateCertificate(caInput);
     } catch (Exception e)  {
         e.printStackTrace();
     } finally {
         try {
             caInput.close();
         } catch (IOException e) {
             e.printStackTrace();
         }
     }

     //创建包含我们证书的KeyStore
     String keyStoreType = KeyStore.getDefaultType();
     KeyStore keyStore = null;
     try {
         keyStore = KeyStore.getInstance(keyStoreType);
         keyStore.load(null, null);
         keyStore.setCertificateEntry("ca", ca);
         String tmfAlgorithm = TrustManagerFactory.getDefaultAlgorithm();

         //创建TrustManager,信任我们的证书
         TrustManagerFactory tmf = TrustManagerFactory.getInstance(tmfAlgorithm);
         tmf.init(keyStore);

         final SSLContext sslContext = SSLContext.getInstance("TLS");
         sslContext.init(null, tmf.getTrustManagers(), null);

         new Thread(new Runnable() {
             @Override
             public void run() {
                 URL url = null;
                 try {
                     url = new URL("https://kyfw.12306.cn/otn");
                     HttpsURLConnection urlConnection = (HttpsURLConnection) url.openConnection();
                     urlConnection.setSSLSocketFactory(sslContext.getSocketFactory());
                     InputStream in = urlConnection.getInputStream();
                     copyInputStreamToOutputStream(in, System.out);
                 } catch (IOException e) {
                     e.printStackTrace();
                 }
             }
         }).start();
     } catch (Exception e) {
         e.printStackTrace();
     }

验证一下，这时候可以正确获取到数据了。

** 证书的服务器端配置
首先明白一个问题，https配置只和web容器有关系，所以https配置和编写服务器的语言没有关系。我们接下来以apache服务器为例，因为申请CA证书比较繁琐，所以我们用自己给自己签名的证书进行测试。

1. 生成密钥

	mkdir /private/etc/apache2/ssl
	cd /private/etc/apache2/ssl
	sudo ssh-keygen -f server.key

2. 生成证书请求文件

	sudo openssl req -new -key server.key -out request.csr

3. 生成ssl证书，使用私钥进行签名

sudo openssl x509 -req -days 365 -in request.csr -signkey server.key -out server.crt

编辑apache的配置文件，放开注释，启用SSL

	LoadModule ssl_module libexec/apache2/mod_ssl.so
	Include /private/etc/apache2/extra/httpd-ssl.conf
	Include /private/etc/apache2/extra/httpd-vhosts.conf

配置apache，指定密钥位置，证书位置：

	SSLCertificateFile "/private/etc/apache2/ssl/server.crt"
	SSLCertificateKeyFile "/private/etc/apache2/ssl/server.key"

好了，我们可以打开测试网址https://127.0.0.1/PhpHttpsTest/查看效果了。跟12306一样。

** SSL/TLS
最后我们来看一些SSL的知识。前面讲到的SSL加密过程只是一个概念，实际的加密过程比较复杂。当然不可能是用公钥来加密通信过程，这样相当耗费时间。

那么SSL是怎么做到的加密传输呢，概括来说是通过SSL握手过程一个“对话秘钥”（session key），用来加密接下来的整个对话过程。

握手过程：

第一步，客户端给出协议版本号、一个客户端生成的随机数，以及客户端支持的加密方法。

第二步，服务端确认双发使用的加密方法，并给出数字证书、以及一个服务端生辰的随机数。

第三步，客户端确认数字证书有效，然后生成一个新的随机数，并使用数字证书中的公钥，加密这个随机数，发给
服务端

第四部，服务端使用自己的私钥，获取客户端发来的随机数

第五部，客户端和服务端根据约定的加密方法，使用前面三个随机数，生成“对话秘钥”，用来
加密接下来的整个对话过程。

** 一些注意点
1. 通常CA不直接提供它的证书，而是提供它的二级证书：<http://developer.android.com/training/articles/security-ssl.html#MissingCa>

这个时候就需要服务端既提供自己的证书，也提供二级证书。因为Android只预存了根证书。

** 问题
1. 双向认证是什么？


好了，还有什么疑问，我们一起探讨下！！

参考：

> SSL介绍：<http://www.ruanyifeng.com/blog/2014/02/ssl_tls.html> <http://www.ruanyifeng.com/blog/2014/09/illustration-ssl.html>

> ssl证书问题：<http://zyan.cc/startssl/>

> andorid官方文档：<http://developer.android.com/training/articles/security-ssl.html#Concepts>

> android中文翻译文档：<http://wiki.jikexueyuan.com/project/android-training-geek/security-ssl.html>
