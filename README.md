<<<<<<< HEAD
# Django后端
=======
## Django 后端
>>>>>>> feature/message

## 环境配置

```bash
conda create -n django_hw python=3.9 -y
conda activate django_hw
```

在此环境的基础之上，你可以运行下述命令安装依赖，注意请确保你的当前工作路径在克隆的小作业仓库中：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 数据库

```bash
python manage.py makemigrations user friend message 
python manage.py migrate
```

### 本地运行
```bash
python3 manage.py runserver
```


```bash
 python3 manage.py makemigrations user friend message conversation && python3 manage.py migrate
```



## 网络请求返回状态码

200 OK：请求成功，服务器成功处理了客户端的请求。

201 Created：请求成功并且服务器创建了新的资源。

204 No Content：请求成功，但服务器不返回任何实体内容。


400 Bad Request：客户端发送的请求有错误，服务器无法理解或处理。

401 Unauthorized：客户端未经身份验证或认证，需要提供有效的凭据。

403 Forbidden：服务器理解请求，但拒绝授权访问所请求的资源。

404 Not Found：请求的资源未在服务器上找到。

405 Method Not Allowed：表示请求方法不被允许或不适用于请求的资源。

410 Gone	资源已经不存在(过去存在)

416 Range Not Satisfiable：	请求的范围无效

424 Failed Dependency:	当前请求失败


500 Internal Server Error：服务器在处理请求时遇到了意外错误。

503 Service Unavailable：服务器暂时无法处理请求，通常是由于过载或维护导致。



## 进行单元测试

```bash
python3 manage.py test
```
