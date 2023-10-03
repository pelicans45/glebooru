"use strict";

const events = require("../events.js");
const views = require("../util/views.js");

const template = views.getTemplate("file-dropper");

const KEY_RETURN = 13;

class FileDropperControl extends events.EventTarget {
    constructor(target, options) {
        super();

        this._options = options;
        const source = template({
            extraText: options.extraText,
            allowMultiple: options.allowMultiple,
            allowUrls: options.allowUrls,
            lock: options.lock,
            id: "file-" + Math.random().toString(36).substring(7),
            urlPlaceholder:
                options.urlPlaceholder || "or paste files/URLs here",
        });

        this._dropperNode = source.querySelector(".file-dropper");
        this._urlInputNode = source.querySelector("input[type=text]");
        this._urlConfirmButtonNode = source.querySelector("button");
        this._fileInputNode = source.querySelector("input[type=file]");
        this._fileInputNode.style.display = "none";

        if (options.allowMultiple) {
            //this._fileInputNode.setAttribute("directory", "");
            //this._fileInputNode.setAttribute("webkitdirectory", "");
            this._fileInputNode.setAttribute("multiple", "");
        }

        this._counter = 0;
        this._dropperNode.addEventListener("dragenter", (e) =>
            this._evtDragEnter(e)
        );
        this._dropperNode.addEventListener("dragleave", (e) =>
            this._evtDragLeave(e)
        );
        this._dropperNode.addEventListener("dragover", (e) =>
            this._evtDragOver(e)
        );
        this._dropperNode.addEventListener("drop", (e) => this._evtDrop(e));
        this._fileInputNode.addEventListener("change", (e) =>
            this._evtFileChange(e)
        );

        /*
        document.addEventListener("keydown", (e) =>
            this._evtUrlInputKeyDown(e)
        );
		*/
        document.addEventListener("paste", (e) => {
            if (document.getElementById("post-upload")) {
                this._evtPaste(e);
            }
        });

        /*
        if (this._urlInputNode) {
            this._urlInputNode.addEventListener("keydown", (e) =>
                this._evtUrlInputKeyDown(e)
            );
            this._urlInputNode.addEventListener("paste", (e) =>
                this._evtPaste(e)
            );
        }
        if (this._urlConfirmButtonNode) {
            this._urlConfirmButtonNode.addEventListener("click", (e) =>
                this._evtUrlConfirmButtonClick(e)
            );
        }
		*/

        this._originalHtml = this._dropperNode.innerHTML;
        views.replaceContent(target, source);
    }

    reset() {
        this._dropperNode.innerHTML = this._originalHtml;
        this.dispatchEvent(new CustomEvent("reset"));
    }

    _emitFiles(files) {
        files = Array.from(files);
        if (this._options.lock) {
            this._dropperNode.innerText = files
                .map((file) => file.name)
                .join(", ");
        }
        this.dispatchEvent(
            new CustomEvent("fileadd", { detail: { files: files } })
        );
    }

    _emitUrls(urls) {
        urls = Array.from(urls).map((url) => url.trim());
        if (this._options.lock) {
            this._dropperNode.innerText = urls
                .map((url) => url.split("/").reverse()[0])
                .join(", ");
        }
        for (let url of urls) {
            if (!url) {
                return;
            }
            if (!url.match(/^https?:\/\/[^.]+\..+$/)) {
                window.alert(`"${url}" does not look like a valid URL.`);
                return;
            }
        }
        this.dispatchEvent(
            new CustomEvent("urladd", { detail: { urls: urls } })
        );
    }

    _evtDragEnter(e) {
        this._dropperNode.classList.add("active");
        this._counter++;
    }

    _evtDragLeave(e) {
        this._counter--;
        if (this._counter === 0) {
            this._dropperNode.classList.remove("active");
        }
    }

    _evtDragOver(e) {
        e.preventDefault();
    }

    _evtFileChange(e) {
        this._emitFiles(e.target.files);
    }

    _evtDrop(e) {
        e.preventDefault();
        this._dropperNode.classList.remove("active");
        if (!e.dataTransfer.files.length) {
            window.alert("Only files are supported.");
        }
        if (!this._options.allowMultiple && e.dataTransfer.files.length > 1) {
            window.alert("Cannot select multiple files.");
        }
        this._emitFiles(e.dataTransfer.files);
    }

    _evtPaste(e) {
        const items = Array.from(
            (e.clipboardData || e.originalEvent.clipboardData).items
        );

        const fileList = items
            .filter((x) => x.kind === "file")
            .map((x) => x.getAsFile())
            .filter((f) => f);

        if (fileList.length > 0) {
            if (!this._options.allowMultiple && fileList.length > 1) {
                window.alert("Cannot select multiple files.");
            } else {
                this._emitFiles(fileList);
            }

            return;
        }

        const urlList = items
            .filter((x) => x.kind === "string")
            .map((x) => x.getAsString().trim())
            .filter((x) => /^https?:\/\/.+/i.test(x));

        const urls = [];

        for (const urlEntry of urlList) {
            urls.push(...urlEntry.split(/[\r\n]/));
        }

        if (urls.length > 0) {
            if (!this._options.allowMultiple && urlList.length > 1) {
                window.alert("Cannot select multiple URLs.");
            } else {
                this._emitUrls(urls);
            }
        }
    }

    _evtUrlInputKeyDown(e) {
        if (e.which !== KEY_RETURN) {
            return;
        }
        e.preventDefault();
        this._dropperNode.classList.remove("active");
        this._emitUrls(this._urlInputNode.value.split(/[\r\n]/));
        this._urlInputNode.value = "";
    }

    _evtUrlConfirmButtonClick(e) {
        e.preventDefault();
        this._dropperNode.classList.remove("active");
        this._emitUrls(this._urlInputNode.value.split(/[\r\n]/));
        this._urlInputNode.value = "";
    }
}

module.exports = FileDropperControl;
