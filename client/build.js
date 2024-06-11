#!/usr/bin/env node
"use strict";

const fs = require("fs");
const yaml = require("js-yaml");
const terser = require("terser");
const underscore = require("underscore");

const DEV = process.env.GLEBOORU_DEV === "1";

const debug = process.argv.includes("--debug");

const outputPath = "/var/www";

function baseUrl() {
    return process.env.BASE_URL ? process.env.BASE_URL : "/";
}

function readTextFile(path) {
    return fs.readFileSync(path, "utf-8");
}

const sharedKeys = [
    "tag_name_regex",
    "tag_category_name_regex",
    "pool_name_regex",
    "pool_category_name_regex",
    "password_regex",
    "user_name_regex",
    "enable_safety",
    "contact_email",
    "can_send_mails",
    "privileges",
    "main_domain",
    "max_suggested_results",
];

const configName = DEV ? "config.dev.yaml" : "config.yaml";
const sitesName = DEV ? "sites.dev.yaml" : "sites.yaml";
const namesName = DEV ? "names.dev.yaml" : "names.yaml";

const serverConf = yaml.load(readTextFile(configName));
const sitesConf = yaml.load(readTextFile(sitesName));
const namesConf = yaml.load(readTextFile(namesName));

serverConf.main_domain = sitesConf.main_domain;
delete sitesConf.main_domain;
serverConf.sites = sitesConf;
serverConf.names = namesConf;

const vars = {};

for (const key of sharedKeys) {
    const camelKey = key.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
    vars[camelKey] = serverConf[key];
}

vars["newPostVisibilityThresholdMilliseconds"] =
    serverConf["new_post_visibility_threshold_minutes"] * 60 * 1000;

const webapp_icons = [
    { name: "android-chrome-192x192.png", size: 192 },
    { name: "android-chrome-512x512.png", size: 512 },
    { name: "apple-touch-icon.png", size: 180 },
    { name: "mstile-150x150.png", size: 150 },
];

const webapp_splash_screens = [
    { w: 640, h: 1136, center: 320 },
    { w: 750, h: 1294, center: 375 },
    { w: 1125, h: 2436, center: 565 },
    { w: 1242, h: 2148, center: 625 },
    { w: 1536, h: 2048, center: 770 },
    { w: 1668, h: 2224, center: 820 },
    { w: 2048, h: 2732, center: 1024 },
];

const external_js = [
    "dompurify",
    "js-cookie",
    "marked",
    "mousetrap",
    "nprogress",
    "superagent",
    "underscore",
];

const baseManifest = {
    icons: [
        {
            src: baseUrl() + "img/android-chrome-192x192.png",
            type: "image/png",
            sizes: "192x192",
        },
        {
            src: baseUrl() + "img/android-chrome-512x512.png",
            type: "image/png",
            sizes: "512x512",
        },
    ],
    start_url: baseUrl(),
    background_color: "#1a1a1a",
    display: "standalone",
};

// -------------------------------------------------

const glob = require("glob");
const path = require("path");
const util = require("util");
const execSync = require("child_process").execSync;
const browserify = require("browserify");
const chokidar = require("chokidar");
const WebSocket = require("ws");
var PrettyError = require("pretty-error");
var pe = new PrettyError();

function gzipFile(file) {
    return;
    file = path.normalize(file);
    execSync(`rm -f ${file}.gz && gzip -6 -k ${file}`);
}

function minifyHtml(html) {
    return require("html-minifier")
        .minify(html, {
            removeComments: true,
            collapseWhitespace: true,
            //conservativeCollapse: true,
        })
        .trim();
}

function bundleHtml(domain, data) {
    let baseHtml = readTextFile("./html/index.html").replace(
        "<!-- Base HTML Placeholder -->",
        `<title>${data.name}</title><base id="base" href="${baseUrl()}"/>`
    );

    baseHtml = baseHtml.replaceAll(
        "$RAND$",
        Math.random().toString(36).substring(7)
    );

    baseHtml = baseHtml.replaceAll("$THEME_COLOR$", data.color);
    fs.writeFileSync(
        `${outputPath}/${domain}/index.html`,
        minifyHtml(baseHtml)
    );

    //console.info("Built HTML");
}

function bundleTemplates() {
    let compiledTemplateJs = [
        `'use strict';`,
        `let _ = require('underscore');`,
        `let templates = {};`,
    ];

    for (const file of glob.sync("./html/**/*.tpl")) {
        const name = path.basename(file, ".tpl").replace(/_/g, "-");
        const placeholders = [];
        let templateText = readTextFile(file);
        templateText = templateText.replace(/<%.*?%>/gi, (match) => {
            const ret = "%%%TEMPLATE" + placeholders.length;
            placeholders.push(match);
            return ret;
        });
        templateText = minifyHtml(templateText);
        templateText = templateText.replace(
            /%%%TEMPLATE(\d+)/g,
            (match, number) => {
                return placeholders[number];
            }
        );

        const functionText = underscore.template(templateText, {
            variable: "ctx",
        }).source;

        compiledTemplateJs.push(`templates['${name}'] = ${functionText};`);
    }
    compiledTemplateJs.push("module.exports = templates;");

    fs.writeFileSync(
        "./js/.templates.autogen.js",
        compiledTemplateJs.join("\n")
    );
    //console.info("Built templates");
}

function bundleCss(domain, data) {
    const stylus = require("stylus");

    function minifyCss(css) {
        return require("csso").minify(css).css;
    }

    const outputDir = `${outputPath}/${domain}/css`;
    const appStylesheet = `${outputDir}/app.css`;
    const customDir = `./sites/${domain}/css`;
    const mainColorLine = `$main-color = ${data.color}\n`;

    let css = "";
    for (const file of glob.sync("./css/**/*.styl")) {
        css += stylus.render(mainColorLine + readTextFile(file), {
            filename: file,
            paths: [customDir],
        });
    }

    const customStyle = `${customDir}/site.styl`;
    css += stylus.render(readTextFile(customStyle), {
        filename: customStyle,
        paths: ["./css"],
    });

    fs.writeFileSync(appStylesheet, minifyCss(css));
    if (process.argv.includes("--gzip")) {
        gzipFile(appStylesheet);
    }

    const vendorStylesheet = `${outputDir}/vendor.css`;

    fs.copyFileSync(
        "./node_modules/line-awesome/dist/line-awesome/css/line-awesome.min.css",
        vendorStylesheet
    );
    if (process.argv.includes("--gzip")) {
        gzipFile(vendorStylesheet);
    }

    //console.info("Built CSS");
}

function minifyJs(path) {
    return terser.minify(fs.readFileSync(path, "utf-8"), {
        compress: { unused: false },
        sourceMap: true,
    }).code;
}

function writeJsBundle(b, path, compress, callback) {
    let outputFile = fs.createWriteStream(path);
    b.bundle()
        .on("error", (e) => console.error(pe.render(e)))
        .pipe(outputFile);
    outputFile.on("finish", () => {
        if (compress) {
			const d = minifyJs(path);
			if (d === undefined) {
				return;
			}
            fs.writeFileSync(path, d);
        }
        callback();
    });
}

function bundleVendorJs(domain, compress) {
    let b = browserify();
    for (let lib of external_js) {
        b.require(lib);
    }

    /*
    if (!process.argv.includes("--no-transpile")) {
        b.add(require.resolve("babel-polyfill"));
    }
	*/

    const file = `${outputPath}/${domain}/js/vendor.js`;
    writeJsBundle(b, file, compress, () => {
        if (process.argv.includes("--gzip")) {
            gzipFile(file);
        }
        //console.info("Built vendor JS");
    });
}

function bundleAppJs(domain, b, compress, callback) {
    const file = `${outputPath}/${domain}/js/app.js`;
    writeJsBundle(b, file, compress, () => {
        if (process.argv.includes("--gzip")) {
            gzipFile(file);
        }
        callback();
    });
}

function bundleJs(domain) {
    if (!process.argv.includes("--no-vendor-js")) {
        bundleVendorJs(domain, true);
    }

    if (!process.argv.includes("--no-app-js")) {
        let b = browserify({ debug: debug });

        /*
        if (!process.argv.includes("--no-transpile")) {
            b = b.transform("babelify");
        }
		*/

        b = b.external(external_js).add(glob.sync("./js/**/*.js"));
        const compress = !debug;
        bundleAppJs(domain, b, compress, () => {
            console.info(`Built ${domain}`);
        });
    }
}

const environment = DEV ? "development" : "production";

function bundleConfig() {
    const config = {
        meta: {
            version: "latest",
            buildDate: new Date().toUTCString(),
        },
        environment: environment,
        sites: serverConf.sites,
        vars: vars,
    };

    fs.writeFileSync("./js/.config.autogen.json", JSON.stringify(config));
    //console.info("Generated config file");
}

function bundleBinaryAssets(domain) {
    const outputDir = `${outputPath}/${domain}`;
    const imgDir = `./sites/${domain}/img`;

    fs.copyFileSync(`${imgDir}/favicon.png`, `${outputDir}/img/favicon.png`);
    //console.info("Copied images");

    fs.copyFileSync(
        "./fonts/open_sans.woff2",
        `${outputDir}/fonts/open_sans.woff2`
    );

    for (let file of glob.sync(
        "./node_modules/line-awesome/dist/line-awesome/fonts/*.*"
    )) {
        if (fs.lstatSync(file).isDirectory()) {
            continue;
        }
        fs.copyFileSync(
            file,
            path.join(`${outputDir}/fonts/`, path.basename(file))
        );
    }
    if (process.argv.includes("--gzip")) {
        for (let file of glob.sync(`${outputDir}/fonts/*.*`)) {
            if (file.endsWith("woff2")) {
                continue;
            }
            gzipFile(file);
        }
    }
    //console.info("Copied fonts");
}

function bundleWebAppFiles(domain, data) {
    const Jimp = require("jimp");

    const outputDir = `${outputPath}/${domain}`;
    const imgDir = `./sites/${domain}/img`;

    const manifest = {
        ...baseManifest,
        name: data.name,
        theme_color: data.color,
    };

    fs.writeFileSync(`${outputDir}/manifest.json`, JSON.stringify(manifest));
    //console.info("Generated app manifest");

    Promise.all(
        webapp_icons.map((icon) => {
            return Jimp.read(`${imgDir}/app.png`).then((file) => {
                file.resize(icon.size, Jimp.AUTO, Jimp.RESIZE_BEZIER).write(
                    path.join(`${outputDir}/img/`, `${icon.name}`)
                );
            });
        })
    ).then(() => {
        //console.info("Generated webapp icons");
    });

    Promise.all(
        webapp_splash_screens.map((dim) => {
            return Jimp.read(`${imgDir}/splash.png`).then((file) => {
                file.resize(dim.center, Jimp.AUTO, Jimp.RESIZE_BEZIER)
                    .background(0xffffffff)
                    .contain(
                        dim.w,
                        dim.center,
                        Jimp.HORIZONTAL_ALIGN_CENTER |
                            Jimp.VERTICAL_ALIGN_MIDDLE
                    )
                    .contain(
                        dim.w,
                        dim.h,
                        Jimp.HORIZONTAL_ALIGN_CENTER |
                            Jimp.VERTICAL_ALIGN_MIDDLE
                    )
                    .write(
                        path.join(
                            `${outputDir}/img/`,
                            "apple-touch-startup-image-" +
                                dim.w +
                                "x" +
                                dim.h +
                                ".png"
                        )
                    );
            });
        })
    ).then(() => {
        //console.info("Generated splash screens");
    });
}

function makeOutputDirs(domain) {
    const dirs = [
        `${outputPath}/${domain}/css`,
        `${outputPath}/${domain}/fonts`,
        `${outputPath}/${domain}/img`,
        `${outputPath}/${domain}/js`,
    ];
    for (let dir of dirs) {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { mode: 0o755, recursive: true });
            console.info("Created directory: " + dir);
        }
    }
}

function watch() {
    let wss = new WebSocket.Server({ port: 9999 });
    const liveReload = !process.argv.includes("--no-live-reload");

    function emitReload(domain) {
        return;

        if (!liveReload) {
            return;
        }
        //console.log("Requesting live reload");
        wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
                if (domain) {
                    client.send("domainreload " + domain);
                } else {
                    client.send("reload");
                }
            }
        });
    }

    if (false) {
        chokidar.watch("./fonts/**/*").on("change", () => {
            try {
                bundleForAllDomains(bundleBinaryAssets, emitReload);
            } catch (e) {
                console.error(pe.render(e));
            }
        });
        chokidar.watch("./img/**/*").on("change", () => {
            try {
                bundleForAllDomains(bundleWebAppFiles, emitReload);
            } catch (e) {
                console.error(pe.render(e));
            }
        });
    }

    chokidar.watch("./html/**/*.tpl").on("change", () => {
        try {
            bundleForAllDomains(bundleHtml, emitReload);
        } catch (e) {
            console.error(pe.render(e));
        }
    });
    chokidar.watch("./css/**/*.styl").on("change", () => {
        try {
            bundleForAllDomains(bundleCss, emitReload);
        } catch (e) {
            console.error(pe.render(e));
        }
    });
    chokidar.watch("./js/**/*.js").on("change", () => {
        try {
            bundleForAllDomains(bundleJs, emitReload);
        } catch (e) {
            console.error(pe.render(e));
        }
    });

    const skipInit = process.argv.includes("--skip-init");
    if (!skipInit) {
        for (const [domain, data] of Object.entries(serverConf.sites)) {
            console.log(`Building ${domain}`);

            if (!process.argv.includes("--no-web-app-files")) {
                bundleWebAppFiles(domain, data);
            }
            if (!process.argv.includes("--no-binary-assets")) {
                bundleBinaryAssets(domain);
            }
            if (!process.argv.includes("--no-html")) {
                bundleHtml(domain, data);
            }
            if (!process.argv.includes("--no-css")) {
                bundleCss(domain, data);
            }
            if (!process.argv.includes("--no-js")) {
                //bundleVendorJs(domain, true);
                bundleJs(domain);
            }
        }
    }

    /*
    let watchify = require("watchify");
    let b = browserify({
        debug: debug,
        entries: ["js/main.js"],
        cache: {},
        packageCache: {},
    });

    b.plugin(watchify);

    /*
    if (!process.argv.includes("--no-transpile")) {
        b = b.transform("babelify");
    }
	*/
    //b = b.external(external_js).add(glob.sync("./js/**/*.js"));

    const compress = false;

    function bundle(id) {
        //console.info("Building JS...");
        let start = new Date();
        for (const domain of Object.keys(serverConf.sites)) {
            bundleAppJs(domain, b, compress, () => {
                emitReload(domain);
                let end = new Date() - start;
                //console.info(`JS for ${domain} rebuilt in %ds`, end / 1000);
                console.info(`Built ${domain}`);
            });
        }
    }

    //b.on("update", bundle);

    if (!skipInit) {
        bundle();
    }
}

function bundleForAllDomains(fn, fn2) {
    for (const [domain, data] of Object.entries(serverConf.sites)) {
        fn(domain, data);
        fn2(domain, data);
        console.info(`Built ${domain}`);
    }
}

// -------------------------------------------------

if (process.argv.includes("--watch")) {
    console.log(
        `Building for ${environment} environment and watching for changes\n`
    );
    //bundleConfig();
    //bundleTemplates();
    watch();
} else {
    console.log(`Building for "${environment}" environment\n`);
    bundleConfig();
    bundleTemplates();
    for (const [domain, data] of Object.entries(serverConf.sites)) {
        console.log(`Building ${domain}`);
        makeOutputDirs(domain);

        if (!process.argv.includes("--no-css")) {
            bundleCss(domain, data);
        }
        if (!process.argv.includes("--no-html")) {
            bundleHtml(domain, data);
        }
        if (!process.argv.includes("--no-web-app-files")) {
            bundleWebAppFiles(domain, data);
        }
        if (!process.argv.includes("--no-binary-assets")) {
            bundleBinaryAssets(domain);
        }
        if (!process.argv.includes("--no-js")) {
            bundleJs(domain);
        }
    }
}
