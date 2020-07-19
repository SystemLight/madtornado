/*
    freedom.js未进行兼容编译，该脚本可配合madtornado ffp协议使用，
    允许你直接在前端产生数据存储到后端服务器文件中，方便读取和写入操作

    使用举例：
    // Freedom{space:空间，代表服务端的一个文件夹，address:请求地址，一般不用特殊设置}
    let freedom = new Freedom({space: "/space"});
    freedom.change("./data.json", {
        onUpdate: (data) => {
            // 接收一个参数，现有的参数内容，返回更新后的内容
            return {author: "SystemLight", version: "V0.1.1"};
        },
        onUpdateEnd: (data) => {
            // 非必须hook函数，当更新完毕后返回更新后的数据内容
        }
    });
 */


let Freedom = (function () {
    let obj = function (options) {
        options = options || {};
        this.address = options.address || "/";
        this.space = options.space || "";
        if (this.address.charAt(this.address.length - 1) === "/") {
            this.address = this.address.substr(0, this.address.length - 1);
        }
    };

    obj.prototype = {
        request: function (path, reqOpt) {
            return fetch(`${this.address}/freedom/file${this.space}${path}`, reqOpt).then(response => {
                if (response.ok) {
                    return response.json();
                }
                return response.json().then(msg => {
                    throw new Error(msg.mssage);
                });
            });
        },
        getJSONData: function (path) {
            return this.request(path, {
                method: "GET"
            });
        },
        addJSONFile: function (path) {
            return this.request(path, {
                method: "POST"
            });
        },
        updateJSONFile: function (path, dataObj) {
            return this.request(path, {
                method: "PUT",
                body: JSON.stringify(dataObj)
            });
        },
        getAllJSONFile: function (path) {
            return this.request(path, {
                method: "GET"
            });
        },
        change(path, hooks) {
            this.getJSONData(path).then(data => {
                let newData = hooks["onUpdate"](data) || {};
                return this.updateJSONFile(path, newData);
            }).then(updateMsg => {
                if (typeof hooks["onUpdateEnd"] === "function") {
                    return this.getJSONData(path).then(data => {
                        hooks["onUpdateEnd"](data);
                    });
                }
            });
        }
    };

    return obj;
})();
