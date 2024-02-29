# Html Convert

一个基于 `FastAPI` 和 `PlayWrite` 的 API 微服务，其主要功能如下：

- 转换 html 代码为 png 图片
- 转换 html 代码为 pdf 文件
- 转换网址 url 为 png 图片
- 转换网址 url 为 pdf 图片
- 转换 json 数据为简易的静态网页

# 部署

已打包为 Docker 镜像。以下为使用 `docker-compose` 部署

```yaml
version: '3.9'
services:
  html_convert:
    image: sqkkyzx/html_convert:latest
    restart: always
    ports:
      - '8080:80'
    volumes:
      - ./html_convert:/usr/src/myapp/tmp
    environment:
      - TZ=Asia/Shanghai
      - ACCESS_ADDRESS=localhost:8080
```

#### 环境变量 `ACCESS_ADDRESS` 说明：

API 将会返回以下格式的数据：

```json
{
  "url": "http://{ACCESS_ADDRESS}/....",
  "filename": "..."
}
```
变量将会影响 `url` 的构成。错误的 `ACCESS_ADDRESS` 会导致无法访问转换的图片。


# 使用

部署后访问主页即可查看 OPENAPI 文档。

# ⚠ 特别警告

没有垃圾清理机制，可以映射到宿主机，使用定时任务或手动清理。