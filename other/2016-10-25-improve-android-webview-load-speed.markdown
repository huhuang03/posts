---
layout: post
title: "Android WeView 加载速度优化"
date: 2016-10-25T16:12:23+08:00
category: 技术
---

# Method1
开启硬件加速

`view.setLayerType(View.LAYER_TYPE_HARDWARE, null);`


# Method2
设置高优先级，但是已经`@deprecated`了，原因是：`It is not recommended to adjust thread priorities, and this will not be supported in future versions.`

`webView.getSettings().setRenderPriority(WebSettings.RenderPriority.HIGH);`

# Method3
启用缓存

```java
webView.getSettings().setCacheMode(WebSettings.LOAD_CACHE_ELSE_NETWORD);
webView.getStrings().setAppCacheEnable(true);
```

可能的值：

`LOAD_CACHE_ELSE_NETWORD` 使用缓存，如果缓存没有过期的话

`LOAD_CACHE_ELSE_NETWORK` 有缓存，不管是否过期

`LOAD_NO_CACHE` 不使用缓存

`LOAD_CACHE_ONLY` 不适用网络，只使用缓存

默认为使用缓存，如果缓存没有过期的话

# Method4
预下载，拦截webView请求，使用本地预下载资源。一整套的解决方法可以参见：[candyWebCache](https://github.com/NEYouFan/ht-candywebcache-android)

下面讲此框架的实现原理：

主要是复写`WebViewClient`的`shouldInterceptRequest(View view, String url)`方法来拦截网络请求

```java
    /**
     * Notify the host application of a resource request and allow the
     * application to return the data.  If the return value is null, the WebView
     * will continue to load the resource as usual.  Otherwise, the return
     * response and data will be used.  NOTE: This method is called on a thread
     * other than the UI thread so clients should exercise caution
     * when accessing private data or the view system.
     *
     * @param view The {@link android.webkit.WebView} that is requesting the
     *             resource.
     * @param url The raw url of the resource.
     * @return A {@link android.webkit.WebResourceResponse} containing the
     *         response information or null if the WebView should load the
     *         resource itself.
     * @deprecated Use {@link #shouldInterceptRequest(WebView, WebResourceRequest)
     *             shouldInterceptRequest(WebView, WebResourceRequest)} instead.
     */
    @Deprecated
    public WebResourceResponse shouldInterceptRequest(WebView view,
            String url) {
        return null;
    }
```

此方法如果返回null，则会请求网络，否则使用返回的WebResourceResponse

框架会通过判断url对应的资源的是否缓存，如果缓存了，则会读入文件，将输入流放入WebResourceResponse中返回

```java
InputStream is = openFileInputStream(findFileByUrl(url));
if (is != null) {
	return new WebResourceResponse(getMimeTypeByUrl(url), "utf-8", is);
}
return null;
```

## `findFileByUrl(url)`规则：
用`http://192.168.1.50:5000/static/hello.js`为例，会先将host先去掉，剩下`static/hello.js`。然后查找文件`cacacheDir/redId/res/static/hello.js`。

## 使用步骤：
1.在Application中初始化

```java
CandyWebCache.getsInstance().init(this, config, "hello", "1.0.1", versionCheckUrl);
```

2.请求更新，服务器会返回缓存文件信息

```json
{
    "data": {
    "resInfos": [
    {
        "userData": "{\"domains\": [\"www.baidu.com\", \"www.163.com\"]}",
        "fullMd5": "13c118e8c0284c0f968883a554bb9dd0",
        "resID": "login",
        "state": 3,
        "resVersion": "20160702",
        "fullUrl": "http://localhost:8000/packages/login_20160702.zip"
    }]
    },
    "code": 200,
    "errMsg": "OK"
}
```

客户端会根据fullUrl下载缓存的资源包

3.如果客户端已经有了旧版本的资源包，则服务器会返回

```json
{
  "data": {
    "resInfos": [
      {
        "userData": "{\"domains\": [\"www.baidu.com\", \"www.163.com\"]}",
        "fullMd5": "9c5a25ced1728d78518e096e9a00bdfb",
        "resID": "login",
        "diffMd5": "5250bcf52d7e259bc4cdd0a12cc059e9",
        "resVersion": "20160703",
        "fullUrl": "http://localhost:8000/packages/login_20160703.zip",
        "diffUrl": "http://localhost:8000/packages/login.diff",
        "state": 1
      }
    ]
  },
  "code": 200,
  "errMsg": "OK"
}
```

此时会下载diffUrl指向的diff包，并将这个diff包apply到旧包上。


## 一些细节问题
1.增量包到底是个什么鬼，如果我修改一个资源之后，需要将这个资源打包上传，还是需要将整包重新上传（版本号增加）？

答：修改一个资源之后需要上传整个包，客户端会下载增量包，然后把增量包apply到旧包上，如果apply失败，客户端会重新下载最新包

2.配置后台上传的时候用到了appId和resId，客户端请求版本数据的时候也要配置appId和resId。这个appId和resId是什么鬼？起什么作用。

答：appId为应用的id，一个服务器可以服务多个应用

redId是为了分domain方便。

3.加密过程是什么?

答：加密是先进行md5编码，在进行des加密，然后进行base64编码。des加密需要一个约定的密钥。服务端会返回加密之后的md5码：

```json
{
    "data": {
    "resInfos": [
    {
        "userData": "{\"domains\": [\"www.baidu.com\", \"www.163.com\"]}",
        "fullMd5": "13c118e8c0284c0f968883a554bb9dd0",
        "resID": "login",
        "state": 3,
        "resVersion": "20160702",
        "fullUrl": "http://localhost:8000/packages/login_20160702.zip"
    }]
    },
    "code": 200,
    "errMsg": "OK"
}
```

客户端将zip包下载下来之后，进行同样的操作，再对比`fullMd5`一样，表示资源没有被篡改。

4.我们在初始化CandyWebCache的时候设置了一个缓存大小，这个缓存是什么缓存，是怎么管理的。

```java
builder.setMemCacheSize(5 * 1025 * 1024);
```

答：这个缓存是内存缓存，不是磁盘缓存，读入文件之后，将此文件内容缓存到内存中。在缓存满需要移除的时候遵循的是先进先出原则。

```java
Iterator<Map.Entry<String, CacheHeader>> iterator = mDataEntries.entrySet().iterator();
while (iterator.hasNext()) {
    Map.Entry<String, CacheHeader> entry = iterator.next();
    CacheHeader e = entry.getValue();
    mTotalSize -= e.data.length;
    iterator.remove();
    ++ prunedFiles;
    if ((mTotalSize + neededSpace) < mMaxCacheSizeInBytes * HYSTERESIS_FACTOR) {
        break;
    }
}
```

`mDataEntries`是一个`LinkedHashMap`。

5.初始化的时候可以设置不缓存的文件类型`builder.setUncachedFileTypes(uncachedType);`，这个文件类型有什么作用？

答：如果请求的文件类型包含在unCachedType中，则不使用缓存，直接请求网络

```java
// in public InputStream getResource(String urlStr)
if (extName != null && mUncachedFileTypes.contains(extName)) {
    WebcacheLog.d("%s", "It is an uncachedFile: " + urlStr);
    return null;
}
```

6. 我们知道domain参与查找的第一个过程，那个是否可以多个资源包配置同一个domain呢，多个资源包能否合并呢。
答：不能合并，一个domain只能拥有一个res

## Tips
1. 资源包命名应该带有版本号。否则会出现应用diff失败的情况。如static_102701.zip
