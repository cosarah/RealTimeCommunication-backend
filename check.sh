docker login registry.secoder.net
# Username 2022010800
# Password liang070800
# 应该会显示 Login Succeeded
docker pull registry.secoder.net/xxx/yyy:master # 把 xxx/yyy 换成本组仓库名，就是你要测试正不正常的那个仓库，下同
docker run -it --rm -p 9090:80 registry.secoder.net/allright/app-backend:dev 