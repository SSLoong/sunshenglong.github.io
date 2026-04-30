---
title: Dart语言基础二：函数
date: 2021-07-27 17:40:11
categories : 
- 技术
tags:
- Dart
---

## 函数

### Functions

Dart 是一种真正面向对象的语言，所以即便函数也是对象并且类型为 [Function](https://api.dart.dev/stable/dart-core/Function-class.html)，这意味着函数可以被赋值给变量或者作为其它函数的参数。你也可以像调用函数一样调用 Dart 类的实例。<!--more-->

下面是定义一个函数的例子：

```dart
bool isNoble(int atomicNumber) {
  return _nobleGases[atomicNumber] != null;
}
```

虽然高效 Dart 指南建议在[公开的 API 上定义返回类型](https://dart.cn/guides/language/effective-dart/design#prefer-type-annotating-public-fields-and-top-level-variables-if-the-type-isnt-obvious)，不过即便不定义，该函数也依然有效：

```dart
isNoble(atomicNumber) {
  return _nobleGases[atomicNumber] != null;
}
```

如果函数体内只包含一个表达式，你可以使用简写语法：

```dart
bool isNoble(int atomicNumber) => _nobleGases[atomicNumber] != null;
```

语法 `=> *表达式*` 是 `{ return *表达式*; }` 的简写， `=>` 有时也称之为胖箭头语法。

 **备忘:**

在 => 与 ; 之间的只能是 *表达式* 而非 *语句*。比如你不能将一个 [if语句](https://dart.cn/guides/language/language-tour#if-and-else) 放在其中，但是可以放置 [条件表达式](https://dart.cn/guides/language/language-tour#conditional-expressions)。

### Parameters

C++ 与 Java 的做法是，提供函数的重载，即提供同名但参数不同的函数。但 Dart 认为重载会导致混乱，因此从设计之初就不支持重载，而是提供了可选命名参数和可选参数。

函数可以有两种形式的参数：**必要参数** 和 **可选参数**。必要参数定义在参数列表前面，可选参数则定义在必要参数后面。可选参数可以是 **命名的** 或 **位置的**。

 **备忘:**

某些 API，特别是 [Flutter](https://flutter.cn/) 控件的构造器，它只使用命名参数，即便参数是强制性的。

### 已命名的参数

已命名的参数是可选参数了，除非他们被特别标记为 required。

当你调用函数时，可以使用 `*参数名*: *参数值*` 的形式来指定命名参数。例如：

```dart
enableFlags(bold: true, hidden: false);
```

定义函数时，使用 `{*param1*, *param2*, …}` 来指定命名参数：

```dart
/// 设置 [bold] 和 [hidden] 标识……
/// Sets the [bold] and [hidden] flags...
void enableFlags({bool bold, bool hidden}) {...}
```

虽然命名参数是可选参数的一种类型，但是你仍然可以使用 [@required](https://pub.flutter-io.cn/documentation/meta/latest/meta/required-constant.html) 注解来标识一个命名参数是必须的参数，此时调用者则必须为该参数提供一个值。例如：

```dart
const Scrollbar({Key key, @required Widget child})
```

如果调用者想要通过 `Scrollbar` 的构造函数构造一个 Scrollbar 对象而不提供 `child` 参数，则会导致编译错误。

[@required](https://pub.flutter-io.cn/documentation/meta/latest/meta/required-constant.html) 注解定义在 [meta](https://pub.flutter-io.cn/packages/meta) package 中，可以直接导入 `package:meta/meta.dart` 包使用。

### 可选的位置参数

使用 `[]` 将一系列参数包裹起来作为位置参数：

```dart
String say(String from, String msg, [String device]) {
  var result = '$from says $msg';
  if (device != null) {
    result = '$result with a $device';
  }
  return result;
}
```

下面是不使用可选参数调用上述函数的示例：

```dart
print(say('Bob', 'Howdy') == 'Bob says Howdy');
```

下面是使用可选参数调用上述函数的示例：

```dart
print(say('Bob', 'Howdy', 'smoke signal') ==
    'Bob says Howdy with a smoke signal');
```



### 默认参数值

可以用 `=` 为函数的命名和位置参数定义默认值，默认值必须为编译时常量，没有指定默认值的情况下默认值为 `null`。

下面是设置可选参数默认值示例：

```dart
/// 设置 [bold] 和 [hidden] 标识……
/// Sets the [bold] and [hidden] flags ...
void enableFlags({bool bold = false, bool hidden = false}) {...}

// bold 的值将为 true；而 hidden 将为 false。
enableFlags(bold: true);
```



在老版本的 Dart 代码中会使用冒号（`:`）而不是 `=` 来设置命名参数的默认值。原因在于刚开始的时候命名参数只支持 `:`。不过现在这个支持已经过时，所以建议现在都 **[使用 `=` 来指定默认值](https://dart.cn/guides/language/effective-dart/usage#do-use--to-separate-a-named-parameter-from-its-default-value)**。

下一个示例将向你展示如何为位置参数设置默认值：

```dart
String say(String from, String msg,
    [String device = 'carrier pigeon', String mood]) {
  var result = '$from says $msg';
  if (device != null) {
    result = '$result with a $device';
  }
  if (mood != null) {
    result = '$result (in a $mood mood)';
  }
  return result;
}

print(say('Bob', 'Howdy') ==
    'Bob says Howdy with a carrier pigeon');
```

List 或 Map 同样也可以作为默认值。下面的示例定义了一个名为 `doStuff()` 的函数，并为其名为 `list` 和 `gifts` 的参数指定了一个 List 类型的值和 Map 类型的值。

```dart
void doStuff(
    {List<int> list = const [1, 2, 3],
    Map<String, String> gifts = const {
      'first': 'paper',
      'second': 'cotton',
      'third': 'leather'
    }}) {
  print('list:  $list');
  print('gifts: $gifts');
}
```

### main() 函数

每个 Dart 程序都必须有一个 `main()` 顶级函数作为程序的入口，`main()` 函数返回值为 `void` 并且有一个 `List` 类型的可选参数。

下面是一个 Web 应用的 `main()` 函数示例：

```dart
void main() {
  querySelector('#sample_text_id')
    ..text = 'Click me!'
    ..onClick.listen(reverseText);
}
```

 **备忘:**

上述代码中的 `..` 语法称之为 [级联调用](https://dart.cn/guides/language/language-tour#cascade-notation-)。使用级联访问可以在一个对象上执行多个操作。

下面是使用命令行访问带参数的 `main()` 函数示例：

```dart
// 使用命令 dart args.dart 1 test 运行该应用
// Run the app like this: dart args.dart 1 test
void main(List<String> arguments) {
  print(arguments);

  print(arguments.length == 2);
  print(int.parse(arguments[0]) == 1);
  print(arguments[1] == 'test');
}
```

你可以通过使用 [参数库](https://pub.flutter-io.cn/packages/args) 来定义和解析命令行参数。

### 函数作为一级对象

可以将函数作为参数传递给另一个函数。例如：

```dart
void printElement(int element) {
  print(element);
}

var list = [1, 2, 3];

// 将 printElement 函数作为参数传递。
list.forEach(printElement);
```

你也可以将函数赋值给一个变量，比如：

```dart
var loudify = (msg) => '!!! ${msg.toUpperCase()} !!!';
print(loudify('hello') == '!!! HELLO !!!');
```

### 匿名函数

大多数方法都是有名字的，比如 `main()` 或 `printElement()`。你可以创建一个没有名字的方法，称之为 *匿名函数*，或 *Lambda表达式* 或 *Closure闭包*。你可以将匿名方法赋值给一个变量然后使用它，比如将该变量添加到集合或从中删除。

匿名方法看起来与命名方法类似，在括号之间可以定义参数，参数之间用逗号分割。

后面大括号中的内容则为函数体：

```
([[*类型*] *参数*[, …]]) { *函数体*;};
```

下面代码定义了只有一个参数 `item` 且没有参数类型的匿名方法。List 中的每个元素都会调用这个函数，打印元素位置和值的字符串：

```dart
var list = ['apples', 'bananas', 'oranges'];
list.forEach((item) {
  print('${list.indexOf(item)}: $item');
});
```

如果函数体内只有一行语句，你可以使用胖箭头缩写法。

```dart
list.forEach(
    (item) => print('${list.indexOf(item)}: $item'));
```

### 词法作用域

Dart 是词法有作用域语言，变量的作用域在写代码的时候就确定了，大括号内定义的变量只能在大括号内访问，与 Java 类似。

下面是一个嵌套函数中变量在多个作用域中的示例：

```dart
bool topLevel = true;

void main() {
  var insideMain = true;

  void myFunction() {
    var insideFunction = true;

    void nestedFunction() {
      var insideNestedFunction = true;

      print(topLevel);
      print(insideMain);
      print(insideFunction);
      print(insideNestedFunction);
    }
  }
}
```

注意 `nestedFunction()` 函数可以访问包括顶层变量在内的所有的变量。

### 词法闭包

*闭包* 即一个函数对象，即使函数对象的调用在它原始作用域之外，依然能够访问在它词法作用域内的变量。

函数可以封闭定义到它作用域内的变量。接下来的示例中，函数 `makeAdder()` 捕获了变量 `addBy`。无论函数在什么时候返回，它都可以使用捕获的 `addBy` 变量。

```dart
/// 返回一个将 [addBy] 添加到该函数参数的函数。
/// Returns a function that adds [addBy] to the
/// function's argument.
Function makeAdder(int addBy) {
  return (int i) => addBy + i;
}

void main() {
  // 生成加 2 的函数。
  var add2 = makeAdder(2);

  // 生成加 4 的函数。
  var add4 = makeAdder(4);

  print(add2(3) == 5);
  print(add4(3) == 7);
}
```

### 测试函数是否相等

下面是顶级函数，静态方法和示例方法相等性的测试示例：

```dart
void foo() {} // 定义顶层函数 (A top-level function)

class A {
  static void bar() {} // 定义静态方法
  void baz() {} // 定义实例方法
}

void main() {
  var x;

  // 比较顶层函数是否相等。
  x = foo;
  print(foo == x);

  // 比较静态方法是否相等。
  x = A.bar;
  print(A.bar == x);

  // 比较实例方法是否相等。
  var v = A(); // A 的实例 #1
  var w = A(); // A 的实例 #2
  var y = w;
  x = w.baz;

  // 这两个闭包引用了相同的实例对象，因此它们相等。
  print(y.baz == x);

  // 这两个闭包引用了不同的实例对象，因此它们不相等。
  print(v.baz != w.baz);
}
```
