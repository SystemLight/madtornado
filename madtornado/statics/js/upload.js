/*
    upload.js未进行兼容编译，该脚本可配合madtornado分片上传解决方案
    实现文件分片上传，同时也可以使用该脚本模块自行定义分片传输协议
    该模块依赖于spark-md5.js

    TODO: 单块数据失败重传，并发数量限制，worker技术进行文件hash运算

    最简单的使用方法
        <input type="file" id="file">
        <button onclick="fd()">按钮</button>
        <script src="./spark-md5.min.js"></script>
        <script src="./upload.js"></script>
        <script>
            let fileEl = document.getElementById("file");

            function fd() {
                upload2madtornado(fileEl, "png", "http://127.0.0.1:8095").then(res => {
                    console.log(res)
                }).catch(err => {
                    console.log("err", err);
                });
            }
        </script>
 */


// 用于和madtornado后端框架便利联动的函数
function upload2madtornado(fileEl, suffix, address) {
    // madtornado后端默认注释该处理路由，请到ancient/view/upload将路由注释取消掉

    let uploadAddress = `${address}/file/upload`;
    let mergeAddress = `${address}/file/merge`;

    // errCode
    // 0:本地没有文件上传
    // 1:上传超时
    // 2:上传合并失败

    let file = fileEl.files[0];
    if (file) {
        let fileMD5;

        // 利用时间换空间对文件首次进行md5计算校验
        return hashFilePromise(file).then(md5 => {
            let fetchList = [];
            fileMD5 = md5;
            // 遍历文件切片生成fetch请求对象
            ffeach(file).forEach((index, data) => {
                fetchList.push(fetchFile(uploadAddress, md5, index, data, 10000));
            });
            return Promise.all(fetchList)
        }).then(function (result) {
            // 当所有数据片传输完毕后，执行的内容
            const params = new URLSearchParams();
            params.append('md5', fileMD5);
            params.append('suffix', suffix);

            return fetchTime(mergeAddress, {
                method: "POST",
                body: params,
            }, 10000).then(response => {
                if (response.ok) {
                    return response.json();
                }
                return Promise.reject({message: "fail", errCode: 2})
            });
        })
    } else {
        return Promise.reject({message: "no file", errCode: 0})
    }
}

// 拥有超时能力的fetch api
function fetchTime(address, init, overTime) {
    // 可以设置超时时间
    return new Promise(function (resolve, reject) {
        setTimeout(function () {
            reject({message: "time out", errCode: 1})
        }, overTime);
        fetch(address, init).then(response => {
            resolve(response);
        });
    });
}


// 请求文件上传
function fetchFile(address, md5, block, data, overTime) {
    let fd = new FormData();

    fd.append("md5", md5);
    fd.append("block", block);
    fd.append("file", data);

    return fetchTime(address, {
        method: "POST",
        body: fd
    }, overTime).then(response => {
        if (response.ok) {
            return response.json();
        }
        return Promise.reject({block, response});
    });
}

// FileForeach对象工厂函数
function ffeach(file, chunkSize) {
    return new FileForeach(file, chunkSize);
}

// 遍历切片数据对象
function FileForeach(file, chunkSize) {
    this.file = file;
    this.chunkSize = chunkSize || 1024 * 1024;
    this.chunks = file.size / this.chunkSize;
    this.currentChunk = 0;
}

FileForeach.prototype.forEach = function (callback) {
    while (!this.isOutRange()) {
        callback(this.currentChunk, this.nextLoad());
    }
};

FileForeach.prototype.isOutRange = function () {
    return this.currentChunk >= this.chunks;
};

FileForeach.prototype.nextLoad = function () {
    let start = this.currentChunk * this.chunkSize;
    let end = (start + this.chunkSize) > this.file.size ? this.file.size : start + this.chunkSize;
    this.currentChunk++;
    return this.file.slice(start, end);
};

// 对文件进行hash运算，算出hash值
function hashFile(file, callback, chunkSize) {
    let fr = new FileReader();
    let spark = new SparkMD5.ArrayBuffer();
    let ff = ffeach(file, chunkSize);

    fr.onload = function (e) {
        spark.append(e.target.result);
        if (!ff.isOutRange()) {
            fr.readAsArrayBuffer(ff.nextLoad());
        } else {
            callback && callback(spark.end(false));
        }
    };

    fr.readAsArrayBuffer(ff.nextLoad());
}

// 对文件进行hash运算，算出hash值，返回Promise对象
function hashFilePromise(file, chunkSize) {
    return new Promise(function (resolve) {
        hashFile(file, (md5) => {
            resolve(md5);
        }, chunkSize);
    });
}
