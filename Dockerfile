FROM python:3.10
WORKDIR /baah
COPY requirements.txt /baah/
RUN sed -i s/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g /etc/apt/sources.list.d/debian.sources && \
apt-get update && \
apt-get install adb libgl1 -y && \
pip config set global.index-url https://mirror.nju.edu.cn/pypi/web/simple && \
pip install -r requirements.txt && \
rm -rf /baah/requirements.txt
EXPOSE 8000
ENTRYPOINT [ "/usr/bin/env", "python3", "/baah/jsoneditor.py", "--host", "0.0.0.0" ]
