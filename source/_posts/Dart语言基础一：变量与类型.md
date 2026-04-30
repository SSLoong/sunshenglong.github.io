---
title: Dart语言基础一：变量与类型
date: 2021-07-15 17:51:01
categories : 
- 技术
tags:
- Dart
---
## 变量

### 变量定义

在 Dart 中，我们可以用 var 或者具体的类型来声明一个变量。当使用 var 定义变量时，表示类型是交由编译器推断决定的，当然你也可以用静态类型去定义变量，更清楚地跟编译器表达你的意图，这样编辑器和编译器就能使用这些静态类型，向你提供代码补全或编译警告的提示了。<!--more-->

- var 是一个关键字，意思是"我不关心这里的类型是什么"，系统会自动判断类型 runtimeType;
- dynamic：动态任意类型，**编译阶段不检查**类型
- Object ：动态任意类型，**编译阶段**检查类型

三者区别：var初始化确定类型后不可更改类型，Object以及dynamic可以更改类型。

在默认情况下，未初始化的变量的值都是 null，因此我们不用担心无法判定一个传递过来的、未定义变量到底是 undefined，还是什么而写一堆冗长的判断语句

### 常量定义

如果你想定义不可变的变量，则需要在定义变量前加上 final 或 const 关键字：

- const，表示变量在编译期间即能确定的值；
- final 则不太一样，用它定义的变量可以在运行时确定值，而一旦确定后就不可再变。

声明 const 常量与 final 常量的典型例子，如下所示：

```dart
final name = 'Andy';
const count = 3;

var x = 70;  
var y = 30;
final z = x / y;
```

**提示：** 实例变量可以是 `final` 类型但不能是 `const` 类型。 必须在构造函数体执行之前初始化 final 实例变量 —— 在变量声明中，参数构造函数中或构造函数的[初始化列表](https://www.dartcn.com/guides/language/language-tour#initializer-list)中进行初始化 。

## 内建类型

Dart 语言支持以下内建类型：

- Number
- String
- Boolean
- List (也被称为 *Array*)
- Map
- Set
- Rune (用于在字符串中表示 Unicode 字符)
- Symbol

这些类型都可以被初始化为字面量。 例如, `'this is a string'` 是一个字符串的字面量， `true` 是一个布尔的字面量。

因为在 Dart 所有的变量终究是一个对象（一个类的实例）， 所以变量可以使用 *构造涵数* 进行初始化。 一些内建类型拥有自己的构造函数。 例如， 通过 `Map()` 来构造一个 map 变量。

### Number

Dart 语言的 Number 有两种类型:

- [int](https://api.dartlang.org/stable/dart-core/int-class.html)

  整数值不大于64位， 具体取决于平台。 在 Dart VM 上， 值的范围从 -263 到 263 - 1. Dart 被编译为 JavaScript 时，使用 [JavaScript numbers,](https://stackoverflow.com/questions/2802957/number-of-bits-in-javascript-numbers/2803010#2803010) 值的范围从 -253 到 253 - 1.

- [double](https://api.dartlang.org/stable/dart-core/double-class.html)

  64位（双精度）浮点数，依据 IEEE 754 标准。

`int` 和 `double` 都是 [`num`.](https://api.dartlang.org/stable/dart-core/num-class.html) 的亚类型。 num 类型包括基本运算 +， -， /， 和 *， 以及 `abs()`，` ceil()`， 和 `floor()`， 等函数方法。  [dart:math](https://api.dartlang.org/stable/dart-math) 库。

整数类型不包含小数点。 下面是定义整数类型字面量的例子:

```
var x = 1;
var hex = 0xDEADBEEF;
```

如果一个数字包含小数点，那么就是小数类型。 下面是定义小数类型字面量的例子:

```
var y = 1.1;
var exponents = 1.42e5;
```

从 Dart 2.1 开始，必要的时候 int 字面量会自动转换成 double 类型。

```
double z = 1; // 相当于 double z = 1.0.
```

**版本提示：** 在 2.1 之前，在 double 上下文中使用 int 字面量是错误的。

以下是将字符串转换为数字的方法，反之亦然：

```
// String -> int
var one = int.parse('1');

// String -> double
var onePointOne = double.parse('1.1');

// int -> String
String oneAsString = 1.toString();

// double -> String
String piAsString = 3.14159.toStringAsFixed(2);
```

int 特有的传统按位运算操作，移位（<<， >>），按位与（&）以及 按位或（|）。 例如：

```
print((3 << 1) == 6); // 0011 << 1 == 0110
print((3 >> 1) == 1); // 0011 >> 1 == 0001
print((3 | 4) == 7); // 0011 | 0100 == 0111
```

数字类型字面量是编译时常量。 在算术表达式中，只要参与计算的因子是编译时常量， 那么算术表达式的结果也是编译时常量。

```
const msPerSecond = 1000;
const secondsUntilRetry = 5;
const msUntilRetry = secondsUntilRetry * msPerSecond;
```

### String

Dart 字符串是一组 UTF-16 单元序列。 字符串通过单引号或者双引号创建。

```
var s1 = 'Single quotes work well for string literals.';
var s2 = "Double quotes work just as well.";
var s3 = 'It\'s easy to escape the string delimiter.';
var s4 = "It's even easier to use the other delimiter.";
```

字符串可以通过 `${`*expression*`}` 的方式内嵌表达式。 如果表达式是一个标识符，则 {} 可以省略。 在 Dart 中通过调用就对象的 `toString()` 方法来得到对象相应的字符串。

```
var s = 'string interpolation';

print('Dart has $s, which is very handy.' ==
    'Dart has string interpolation, ' +
        'which is very handy.');
print('That deserves all caps. ' +
        '${s.toUpperCase()} is very handy!' ==
    'That deserves all caps. ' +
        'STRING INTERPOLATION is very handy!');
```

**提示：** `==` 运算符用来测试两个对象是否相等。 在字符串中，如果两个字符串包含了相同的编码序列，那么这两个字符串相等。

可以使用 `+` 运算符来把多个字符串连接为一个，也可以把多个字面量字符串写在一起来实现字符串连接：

```
var s1 = 'String '
    'concatenation'
    " works even over line breaks.";
print(s1 ==
    'String concatenation works even over '
    'line breaks.');

var s2 = 'The + operator ' + 'works, as well.';
print(s2 == 'The + operator works, as well.');
```

使用连续三个单引号或者三个双引号实现多行字符串对象的创建：

```
var s1 = '''
You can create
multi-line strings like this one.
''';

var s2 = """This is also a
multi-line string.""";
```

使用 `r` 前缀，可以创建 “原始 raw” 字符串：

```
var s = r"In a raw string, even \n isn't special.";
```

参考 [Runes](https://www.dartcn.com/guides/language/language-tour#runes) 来了解如何在字符串中表达 Unicode 字符。

一个编译时常量的字面量字符串中，如果存在插值表达式，表达式内容也是编译时常量， 那么该字符串依旧是编译时常量。 插入的常量值类型可以是 null，数值，字符串或布尔值。

```
// const 类型数据
const aConstNum = 0;
const aConstBool = true;
const aConstString = 'a constant string';

// 非 const 类型数据
var aNum = 0;
var aBool = true;
var aString = 'a string';
const aConstList = [1, 2, 3];

const validConstString = '$aConstNum $aConstBool $aConstString'; //const 类型数据
// const invalidConstString = '$aNum $aBool $aString $aConstList'; //非 const 类型数据
```

更多关于 string 的使用, 参考 [字符串和正则表达式](https://www.dartcn.com/guides/libraries/library-tour#strings-and-regular-expressions).

### Boolean

Dart 使用 `bool` 类型表示布尔值。 Dart 只有字面量 `true` and `false` 是布尔类型， 这两个对象都是编译时常量。

Dart 的类型安全意味着不能使用 `if (*nonbooleanValue*)` 或者 `print (*nonbooleanValue*)`。 而是应该像下面这样，明确的进行值检查：

```
// 检查空字符串。
var fullName = '';
print(fullName.isEmpty);

// 检查 0 值。
var hitPoints = 0;
print(hitPoints <= 0);

// 检查 null 值。
var unicorn;
print(unicorn == null);

// 检查 NaN 。
var iMeantToDoThis = 0 / 0;
print(iMeantToDoThis.isNaN);
```

### List

几乎每种编程语言中最常见的集合可能是 *array* 或有序的对象集合。 在 Dart 中的 *Array* 就是 [List](https://api.dartlang.org/stable/dart-core/List-class.html) 对象， 通常称之为 *List* 。

Dart 中的 List 字面量非常像 JavaScript 中的 array 字面量。 下面是一个 Dart List 的示例：

```
var list = [1, 2, 3];
```

**提示：** Dart 推断 `list` 的类型为 `List<int>` 。 如果尝试将非整数对象添加到此 List 中， 则分析器或运行时会引发错误。 有关更多信息，请阅读 [类型推断。](https://www.dartcn.com/guides/language/sound-dart#type-inference)

Lists 的下标索引从 0 开始，第一个元素的索引是 0。 list.length - 1 是最后一个元素的索引。 访问 List 的长度和元素与 JavaScript 中的用法一样：

```
var list = [1, 2, 3];
print(list.length == 3);
print(list[1] == 2);

list[1] = 1;
print(list[1] == 1);
```

在 List 字面量之前添加 const 关键字，可以定义 List 类型的编译时常量：

```
var constantList = const [1, 2, 3];
// constantList[1] = 1; // 取消注释会引起错误。
```

List 类型包含了很多 List 的操作函数。 更多信息参考 [泛型](https://www.dartcn.com/guides/language/language-tour#generics) 和 [集合](https://www.dartcn.com/guides/libraries/library-tour#collections).

### Set

在 Dart 中 Set 是一个元素唯一且无需的集合。 Dart 为 Set 提供了 Set 字面量和 [Set](https://api.dartlang.org/stable/dart-core/Set-class.html) 类型。

**版本提示：** 虽然 Set *类型* 一直是 Dart 的核心部分， 但在 Dart2.2 中才引入了 Set *字面量* 。

下面是通过字面量创建 Set 的一个简单示例：

```
var halogens = {'fluorine', 'chlorine', 'bromine', 'iodine', 'astatine'};
```

**Note:** Dart 推断 `halogens` 类型为 `Set<String>` 。如果尝试为它添加一个 错误类型的值，分析器或执行时会抛出错误。更多内容，参阅 [类型推断](https://www.dartcn.com/guides/language/sound-dart#type-inference)。

要创建一个空集，使用前面带有类型参数的 `{}` ，或者将 `{}` 赋值给 `Set` 类型的变量：

```
var names = <String>{};
// Set<String> names = {}; // 这样也是可以的。
// var names = {}; // 这样会创建一个 Map ，而不是 Set 。
```

**是 Set 还是 Map ？** Map 字面量语法同 Set 字面量语法非常相似。 因为先有的 Map 字母量语法，所以 `{}` 默认是 `Map` 类型。   如果忘记在 `{}` 上注释类型或赋值到一个未声明类型的变量上，   那么 Dart 会创建一个类型为 `Map<dynamic, dynamic>` 的对象。

使用 `add()` 或 `addAll()` 为已有的 Set 添加元素：

```
var elements = <String>{};
elements.add('fluorine');
elements.addAll(halogens);
```

使用 `.length` 来获取 Set 中元素的个数：

```
var elements = <String>{};
elements.add('fluorine');
elements.addAll(halogens);
print(elements.length == 5);
```

在 Set 字面量前增加 `const` ，来创建一个编译时 Set 常量：

```
final constantSet = const {
  'fluorine',
  'chlorine',
  'bromine',
  'iodine',
  'astatine',
};
// constantSet.add('helium'); // Uncommenting this causes an error.
```

更多关于 Set 的内容，参阅 [Generic](https://www.dartcn.com/guides/language/language-tour#generics) 及 [Set](https://www.dartcn.com/guides/libraries/library-tour#sets)。

### Map

通常来说， Map 是用来关联 keys 和 values 的对象。 keys 和 values 可以是任何类型的对象。在一个 Map 对象中一个 *key* 只能出现一次。 但是 *value* 可以出现多次。 Dart 中 Map 通过 Map 字面量 和 [Map](https://api.dartlang.org/stable/dart-core/Map-class.html) 类型来实现。

下面是使用 Map 字面量的两个简单例子：

```
var gifts = {
  // Key:    Value
  'first': 'partridge',
  'second': 'turtledoves',
  'fifth': 'golden rings'
};

var nobleGases = {
  2: 'helium',
  10: 'neon',
  18: 'argon',
};
```

**提示：** Dart 会将 `gifts` 的类型推断为 `Map<String, String>`， `nobleGases` 的类型推断为 `Map<int, String>` 。 如果尝试在上面的 map 中添加错误类型，那么分析器或者运行时会引发错误。 有关更多信息，请阅读[类型推断。](https://www.dartcn.com/guides/language/sound-dart#type-inference)。

以上 Map 对象也可以使用 Map 构造函数创建：

```
var gifts = Map();
gifts['first'] = 'partridge';
gifts['second'] = 'turtledoves';
gifts['fifth'] = 'golden rings';

var nobleGases = Map();
nobleGases[2] = 'helium';
nobleGases[10] = 'neon';
nobleGases[18] = 'argon';
```

**提示:** 这里为什么只有 `Map()` ，而不是使用 `new Map()`。 因为在 Dart 2 中，`new` 关键字是可选的。 有关更多信息，参考 [构造函数的使用](https://www.dartcn.com/guides/language/language-tour#%E4%BD%BF%E7%94%A8%E6%9E%84%E9%80%A0%E5%87%BD%E6%95%B0)。

类似 JavaScript ，添加 key-value 对到已有的 Map 中：

```
var gifts = {'first': 'partridge'};
gifts['fourth'] = 'calling birds'; // Add a key-value pair
```

类似 JavaScript ，从一个 Map 中获取一个 value：

```
var gifts = {'first': 'partridge'};
print(gifts['first'] == 'partridge');
```

如果 Map 中不包含所要查找的 key，那么 Map 返回 null：

```
var gifts = {'first': 'partridge'};
print(gifts['fifth'] == null);
```

使用 `.length` 函数获取当前 Map 中的 key-value 对数量：

```
var gifts = {'first': 'partridge'};
gifts['fourth'] = 'calling birds';
print(gifts.length == 2);
```

创建 Map 类型运行时常量，要在 Map 字面量前加上关键字 `const`。

```
final constantMap = const {
  2: 'helium',
  10: 'neon',
  18: 'argon',
};

// constantMap[2] = 'Helium'; // 取消注释会引起错误。
```

更名多关于 Map 的内容，参考 [Generics](https://www.dartcn.com/guides/language/language-tour#generics) and [Maps](https://www.dartcn.com/guides/libraries/library-tour#maps).

### Rune

在 Dart 中， Rune 用来表示字符串中的 UTF-32 编码字符。

Unicode 定义了一个全球的书写系统编码， 系统中使用的所有字母，数字和符号都对应唯一的数值编码。 由于 Dart 字符串是一系列 UTF-16 编码单元， 因此要在字符串中表示32位 Unicode 值需要特殊语法支持。

表示 Unicode 编码的常用方法是， `\uXXXX`, 这里 XXXX 是一个4位的16进制数。 例如，心形符号 (♥) 是 `\u2665`。 对于特殊的非 4 个数值的情况， 把编码值放到大括号中即可。 例如，emoji 的笑脸 (😊) 是 `\u{1f600}`。

[String](https://api.dartlang.org/stable/dart-core/String-class.html) 类有一些属性可以获得 rune 数据。 属性 `codeUnitAt` 和 `codeUnit` 返回16位编码数据。 属性 `runes` 获取字符串中的 Rune 。

**提示：** 谨慎使用 list 方式操作 Rune 。 这种方法很容易引发崩溃， 具体原因取决于特定的语言，字符集和操作。 有关更多信息，参考 [How do I reverse a String in Dart?](http://stackoverflow.com/questions/21521729/how-do-i-reverse-a-string-in-dart) on Stack Overflow.

### Symbol

一个 Symbol 对象表示 Dart 程序中声明的运算符或者标识符。 你也许永远都不需要使用 Symbol ，但要按名称引用标识符的 API 时， Symbol 就非常有用了。 因为代码压缩后会改变标识符的名称，但不会改变标识符的符号。 通过字面量 Symbol ，也就是标识符前面添加一个 `#` 号，来获取标识符的 Symbol 。

```
#radix
#bar
```

Symbol 字面量是编译时常量。
