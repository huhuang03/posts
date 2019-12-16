---
layout: post
title: "elf analysis"
date: 2017-04-09T10:08:24+08:00
category: "技术"
---

# ELF格式分析

本文完全参考下面的引用。做一个总结和记录。

## 基础知识
elf是一种文件格式，用于存储Linux程序。所以说想明白elf格式，我们就应该了解一下计算机执行程序需要的哪些信息。所以这一节，我们看一下计算机系统的基础知识。
Linux系统给每个进城分配了4G的空间。一个地址可以存储1Byte的信息。1G需要1024 * 1024 * 1024个Byte。也就是需要1024 * 1024 * 1024个寻址空间。也即是`hex(1024 * 1024 * 1024) = 0x40000000`个地址。4G就是`hex(1024 * 1024 * 1024 * 4) = 0x100000000`这么多寻址空间。其中 0xC0000000到0xFFFFFFFF 这个地址段是留给系统使用的，主要用于系统（linux 内核)和进程通信和交换数据，   用户可以使用3GB的空间从(0x00000000-0xBFFFFFFF)。

其实计算机的内存是没有那么大的，比如我们实际使用的计算机只有2G,以前更小，只有几百M,而且一台计算机上不只运行一个进程，一个占用4G，如果有10个进程，那就得着用40G了，哪有那么打的内存呢？其实这个不要紧，因为操作系统分配给用户的是虚拟内存，程序要可以使用3个G的内存。至于操作系统怎样把虚拟内存转化成物理内存，对于开发应用程序的工程师来说，是不需要了解的。我们直接使用虚拟内存就可以了，而不用担心其它进程会侵犯到你的内存空间。

## 可执行的ELF文件
elf文件分为三种类型：
* 目标文件 (A `recolatable` file holds code and data suitable for linking with other object files to creat an executable or a shared object file.)
* 可执行文件（我们的运行文件）
* 动态库 (A `shared object` file holds code and data suitable for linking in tow context. Fist, the link editor [see ld(SD_CMD)]
may process it with other relocatable and shared object files to create another object file. Second, the dynamic linker combines it with an executable file and other shared objects to create a process image.)

## 文件格式
![Elf file format](/images/elf_file_format.png)

### 数据类型
32 位数据类型

Name | Size | Alignment | Purpose
--- | --- | --- |
Elf32_Addr | 4 | 4 | Unsinged program address
Elf32_Harf | 2 | 2 | Unsigned medium integer
Elf32_Off | 4 | 4 | Unsinged file offset
Elf32_Sword | 4 | 4 | Signed large integer
unsinged char | 1 | 1 | Unsigned small integer





### 可执行文件
可执行文件一般分为4个部分，能够进行拓展。我们理解这4个部分就可以了。
1. elf 文件头(ELF header)，这个文件头是对elf文件整体信息的描述，在32位系统下是52个字节。在64位紫铜下是64个字节。
对于可执行文件来说，文件头包含的以下信息与进城启动有关
```
e_entry 程序入口地址
e_phoff segment偏移
e_phnum segment数量
```
2. Segment表（Program header table) 这个表是加载指示器，加载Segment段的指示器。 该表的数据结构如下
```
typedef struct
{
	Elf64_Word p_type   // setmengt type	
	Elf64_Word p_flags  // Segment flasgs 像linux权限。124 可执行，可写，可读
	Elf64_Off p_offset; // segment file offset 段在文件中的便宜
	Elf64_Addr p_vaddr; // Segment virtual address 虚拟内存地址，这个表示内存中的
	Elf64_Addr p_paddr; // Segment physical address 物理内存地址，对应用程序来说，这个字段无用
	Elf64_Xword p_filesz; // Segment size in file 段在文件中的长度
	Elf64_Wword p_memsz;  // Segment size in memory 段在内存的长度 一个和段在文件的长度一样
	Elf64_Wword p_align;  // Segment alignment 段对齐
} Elf64_Phdr;
```
3. Segments，对可执行文件来说，最重要的就是数据段和代码段
4. sections header table。对可执行文件来说。没有用到。对Link file来说。是section的描述表。

把以上信息删掉，然后读这个文章。[elf 格式下载](www.skyfree.org/linux/references/ELF_Format.pdf)
其实完全可以参考linux内核的代码中的elf：[elf source](https://github.com/torvalds/linux/blob/master/include/uapi/linux/elf.h)

### String table
section的名称存在在shstr section这个区段中。这个区段在哪里呢？
我们可以根据head中的e_shstrndx来确定shstr section在所有section中的位置。



来源：
> http://blog.csdn.net/hhhbbb/article/details/6855004
> 
