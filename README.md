## ULinkMe

![PyPI](https://img.shields.io/pypi/v/ulinkme?style=flat-square) ![GitHub](https://img.shields.io/github/license/Hyiker/ULinkMe?style=flat-square)

一个用于自动为指定文件夹内的所有文件实时递归创建硬链接的跨平台工具

A cross-platform tool for automatically creating hard links recursively in real time for all files in a given folder

### Usage 使用



1. 使用pip下载ulinkme
Use pip to download ulinkme

```bash
pip install ulinkme
```

2. 创建json配置文件，一份示例配置参照[config.example.json](config.example.json)
Create a json configuration file, a sample configuration reference [config.example.json](config.example.json)

3. 运行ulinkme
Run ulinkme

```bash
ulinkme ./config.json
```

### Configuration 配置文件

| 键值             | 类型 / 默认值                 | 说明                                                               |
| ---------------- | ----------------------------- | ------------------------------------------------------------------ |
| `log.level`      | `String` / `warning`          | 日志的等级，可选debug/info/warning/errorg                          |
| `log.logdir`     | `String` / `None`             | 日志的输出目录，不填写则输出至标准流中                             |
| `links`          | `list[Link]` / `[]`           | 描述链接目录的对象列表                                             |
| `Link.target`    | `String` / required           | 链接的目标文件夹名，如果不存在则会自动创建                         |
| `Link.name`      | `String` / required           | 链接的文件夹名，我们将会创建形如`name->target`的硬链接             |
| `Link.recursive` | `Bool` / `true`               | 是否递归链接文件夹下的文件，目前只支持文件夹到文件夹的递归链接     |
| `Link.events`    | `list[String]` / `["create"]` | 同步两个文件夹下的哪些操作，目前支持的有`create`, `move`, `delete` |

| Key              | Value Type / Default Value    | Description                                                                                                     |
| ---------------- | ----------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `log.level`      | `String` / `warning`          | The level of the log, optional debug/info/warning/error                                                         |
| `log.logdir`     | `String` / `None`             | The output directory of the logs, or to the standard stream if not filled in                                    |
| `links`          | `list[Link]` / `[]`           | List of objects describing the linked directory                                                                 |
| `Link.target`    | `String` / required           | Target folder name of the link, create automatically if doesn't exist                                           |
| `Link.name`      | `String` / required           | For the linked folder name, we will create a hard link like `name->target`                                      |
| `Link.recursive` | `Bool` / `true`               | Whether to recursively link files under folders, currently only folder-to-folder recursive linking is supported |
| `Link.events`    | `list[String]` / `["create"]` | What operations are synchronized under two folders, currently supported are `create`, `move`, `delete`          |

### LICENSE 协议

项目使用MIT LICENSE开源

The project is licensed under MIT LICENSE
