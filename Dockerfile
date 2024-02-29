FROM python:3.12-slim

WORKDIR /usr/src/myapp

# 安装依赖
RUN mkdir -p /usr/src/myapp/tmp/pdf && mkdir /usr/src/myapp/tmp/png \
    && pip install --upgrade pip \
    && pip install requests fastapi uvicorn playwright \
    && pip cache purge

RUN apt-get update \
    && playwright install chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|' /etc/apt/sources.list.d/debian.sources && \
    apt-get update \
    && playwright install-deps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 更多依赖库安装
RUN pip install --upgrade pip && pip install toml && pip cache purge

COPY myapp/main.py /usr/src/myapp/

# 启动应用程序
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]