---
title: Dart语言基础三：运算符
date: 2021-07-31 14:42:59
categories : 
- 技术
tags:
- Dart
---

## 运算符

Dart 和绝大部分编程语言的运算符一样，所以我们可以用熟悉的方式去执行程序代码运算。不过，**Dart 多了几个额外的运算符，用于简化处理变量实例缺失（即 null）的情况。**<!--more-->

- ?. 运算符：假设 Point 类有 printInfo() 方法，p 是 Point 的一个可能为 null 的实例。那么，p 调用成员方法的安全代码，可以简化为 p?.printInfo() ，表示 p 为 null 的时候跳过，避免抛出异常。
- ??= 运算符：如果 a 为 null，则给 a 赋值 value，否则跳过。这种用默认值兜底的赋值语句在 Dart 中我们可以用 a ??= value 表示。
- ?? 运算符：如果 a 不为 null，返回 a 的值，否则返回 b。在 Java 或者 C++ 中，我们需要通过三元表达式 (a != null)? a : b 来实现这种情况。而在 Dart 中，这类代码可以简化为 a ?? b。

**在 Dart 中，一切都是对象，就连运算符也是对象成员函数的一部分。**

对于系统的运算符，一般情况下只支持基本数据类型和标准库中提供的类型。而对于用户自定义的类，如果想支持基本操作，比如比较大小、相加相减等，则需要用户自己来定义关于这个运算符的具体实现。

**Dart 提供了类似 C++ 的运算符覆写机制**，使得我们不仅可以覆写方法，还可以覆写或者自定义运算符。

可以看一个 Vector 类中自定义“+”运算符和覆写"=="运算符的例子：

```dart

class Vector {
  num x, y;
  Vector(this.x, this.y);
  // 自定义相加运算符，实现向量相加
  Vector operator +(Vector v) =>  Vector(x + v.x, y + v.y);
  // 覆写相等运算符，判断向量相等
  bool operator == (dynamic v) => x == v.x && y == v.y;
}

final x = Vector(3, 3);
final y = Vector(2, 2);
final z = Vector(1, 1);
print(x == (y + z)); //  输出true

```

operator 是 Dart 的关键字，与运算符一起使用，表示一个类成员运算符函数。在理解时，我们应该把 operator 和运算符作为整体，看作是一个成员函数名。

### 算术运算符

Dart 支持常用的算术运算符：

| 运算符      | 描述                                       |
| ----------- | ------------------------------------------ |
| `+`         | 加                                         |
| `–`         | 减                                         |
| `-*表达式*` | 一元负, 也可以作为反转（反转表达式的符号） |
| `*`         | 乘                                         |
| `/`         | 除                                         |
| `~/`        | 除并取整                                   |
| `%`         | 取模                                       |

示例：

```dart
print(2 + 3);
print(2 - 3);
print(2 * 3);
print(5 / 2); // 结果是一个浮点数
print(5 ~/ 2); // 结果是一个整数
print(5 % 2); // 取余

print('5/2 = ${5 ~/ 2} r ${5 % 2}');
```

Dart 还支持自增自减操作。

| Operator`++*var*` | `*var* = *var* + 1` (表达式的值为 `*var* + 1`) |
| ----------------- | ---------------------------------------------- |
| `*var*++`         | `*var* = *var* + 1` (表达式的值为 `*var*`)     |
| `--*var*`         | `*var* = *var* – 1` (表达式的值为 `*var* – 1`) |
| `*var*--`         | `*var* = *var* – 1` (表达式的值为 `*var*`)     |

示例：

```dart
var a, b;

a = 0;
b = ++a; // 在 b 赋值前将 a 增加 1。
print(a == b); // 1 == 1

a = 0;
b = a++; // 在 b 赋值后将 a 增加 1。
print(a != b); // 1 != 0

a = 0;
b = --a; // 在 b 赋值前将 a 减少 1。
print(a == b); // -1 == -1

a = 0;
b = a--; // 在 b 赋值后将 a 减少 1。
print(a != b); // -1 != 0
```

### 关系运算符

下表列出了关系运算符及含义：

| Operator`==` | 相等     |
| ------------ | -------- |
| `!=`         | 不等     |
| `>`          | 大于     |
| `<`          | 小于     |
| `>=`         | 大于等于 |
| `<=`         | 小于等于 |

要判断两个对象 x 和 y 是否表示相同的事物使用 `==` 即可。（在极少数情况下，可能需要使用 [identical()](https://api.dart.dev/stable/dart-core/identical.html) 函数来确定两个对象是否完全相同。）。下面是 `==` 运算符的一些规则：

1. 假设有变量 *x* 和 *y*，且 x 和 y 至少有一个为 null，则当且仅当 x 和 y 均为 null 时 x == y 才会返回 true，否则只有一个为 null 则返回 false。
2. `*x*.==(*y*)` 将会返回值，这里不管有没有 y，即 y 是可选的。也就是说 `==` 其实是 x 中的一个方法，并且可以被重写。详情请查阅[重写运算符](https://dart.cn/guides/language/language-tour#overridable-operators)。

下面的代码给出了每一种关系运算符的示例：

```dart
print(2 == 2);
print(2 != 3);
print(3 > 2);
print(2 < 3);
print(3 >= 3);
print(2 <= 3);
```

### 类型判断运算符

`as`、`is`、`is!` 运算符是在运行时判断对象类型的运算符。

| Operator`as` | 类型转换（也用作指定[类前缀](https://dart.cn/guides/language/language-tour#specifying-a-library-prefix))） |
| ------------ | ------------------------------------------------------------ |
| `is`         | 如果对象是指定类型则返回 true                                |
| `is!`        | 如果对象是指定类型则返回 false                               |

当且仅当 `obj` 实现了 `T` 的接口，`obj is T` 才是 true。例如 `obj is Object` 总为 true，因为所有类都是 Object 的子类。

仅当你确定这个对象是该类型的时候，你才可以使用 `as` 操作符可以把对象转换为特定的类型。例如：

```dart
(emp as Person).firstName = 'Bob';
```

如果你不确定这个对象类型是不是 `T`，请在转型前使用 `is T` 检查类型。

```dart
if (emp is Person) {
  // 类型检查
  emp.firstName = 'Bob';
}
```

你可以使用 `as` 运算符进行缩写：

```dart
(emp as Person).firstName = 'Bob';
```

 **备忘:**

上述两种方式是有区别的：如果 `emp` 为 null 或者不为 Person 类型，则第一种方式将会抛出异常，而第二种不会。

### 赋值运算符

可以使用 `=` 来赋值，同时也可以使用 `??=` 来为值为 null 的变量赋值。

```dart
// 将 value 赋值给 a (Assign value to a)
a = value;
// 当且仅当 b 为 null 时才赋值
b ??= value;
```

像 `+=` 这样的赋值运算符将算数运算符和赋值运算符组合在了一起。

| `=`  | `–=` | `/=`  | `%=`  | `>>=` | `^=` |
| ---- | ---- | ----- | ----- | ----- | ---- |
| `+=` | `*=` | `~/=` | `<<=` | `&=`  | `|=` |

下表解释了符合运算符的原理：

| 场景                      | 复合运算    | 等效表达式     |
| ------------------------- | ----------- | -------------- |
| **假设有运算符 \*op\*：** | `a *op*= b` | `a = a *op* b` |
| **示例：**                | `a += b`    | `a = a + b`    |

下面的例子展示了如何使用赋值以及复合赋值运算符：

```dart
var a = 2; // 使用 = 赋值 (Assign using =)
a *= 3; // 赋值并做乘法运算 Assign and multiply: a = a * 3
print(a == 6);
```

### 逻辑运算符

使用逻辑运算符你可以反转或组合布尔表达式。

| 运算符      | 描述                                                      |
| ----------- | --------------------------------------------------------- |
| `!*表达式*` | 对表达式结果取反（即将 true 变为 false，false 变为 true） |
| `||`        | 逻辑或                                                    |
| `&&`        | 逻辑与                                                    |

下面是使用逻辑表达式的示例：

```dart
if (!done && (col == 0 || col == 3)) {
  // ...Do something...
}
```

### 按位和移位运算符

在 Dart 中，二进制位运算符可以操作二进制的某一位，但仅适用于整数。

| 运算符      | 描述                                        |
| ----------- | ------------------------------------------- |
| `&`         | 按位与                                      |
| `|`         | 按位或                                      |
| `^`         | 按位异或                                    |
| `~*表达式*` | 按位取反（即将 “0” 变为 “1”，“1” 变为 “0”） |
| `<<`        | 位左移                                      |
| `>>`        | 位右移                                      |

下面是使用按位和移位运算符的示例：

```dart
final value = 0x22;
final bitmask = 0x0f;

print((value & bitmask) == 0x02); // 按位与 (AND)
print((value & ~bitmask) == 0x20); // 取反后按位与 (AND NOT)
print((value | bitmask) == 0x2f); // 按位或 (OR)
print((value ^ bitmask) == 0x2d); // 按位异或 (XOR)
print((value << 4) == 0x220); // 位左移 (Shift left)
print((value >> 4) == 0x02); // 位右移 (Shift right)
```

### 条件表达式

Dart 有两个特殊的运算符可以用来替代 [if-else](https://dart.cn/guides/language/language-tour#if-和-else) 语句：

- `*condition* ? *expr1* : *expr2*`

  If *condition* is true, evaluates *expr1* (and returns its value); otherwise, evaluates and returns the value of *expr2*.

`*条件* ? *表达式 1* : *表达式 2*` ：如果条件为 true，执行表达式 1并返回执行结果，否则执行表达式 2 并返回执行结果。

- `*expr1* ?? *expr2*`

  If *expr1* is non-null, returns its value; otherwise, evaluates and returns the value of *expr2*.

`*表达式 1* ?? *表达式 2*`：如果表达式 1 为非 null 则返回其值，否则执行表达式 2 并返回其值。

如果赋值是根据布尔表达式则考虑使用 `?:`。

```dart
var visibility = isPublic ? 'public' : 'private';
```

如果赋值是根据判定是否为 null 则考虑使用 `??`。

```dart
String playerName(String name) => name ?? 'Guest';
```

上述示例还可以写成至少下面两种不同的形式，只是不够简洁：

```dart
// 相对使用 ?: 运算符来说稍微长了点。(Slightly longer version uses ?: operator).
String playerName(String name) => name != null ? name : 'Guest';

// 如果使用 if-else 则更长。
String playerName(String name) {
  if (name != null) {
    return name;
  } else {
    return 'Guest';
  }
}
```



### 级联运算符（..）

级联运算符（`..`）可以让你在同一个对象上连续调用多个对象的变量或方法。

比如下面的代码：

```dart
querySelector('#confirm') // 获取对象 (Get an object).
  ..text = 'Confirm' // 使用对象的成员 (Use its members).
  ..classes.add('important')
  ..onClick.listen((e) => window.alert('Confirmed!'));
```

第一个方法 `querySelector` 返回了一个 Selector 对象，后面的级联操作符都是调用这个 Selector 对象的成员并忽略每个操作的返回值。

上面的代码相当于：

```dart
var button = querySelector('#confirm');
button.text = 'Confirm';
button.classes.add('important');
button.onClick.listen((e) => window.alert('Confirmed!'));
```

级联运算符可以嵌套，例如：

```dart
final addressBook = (AddressBookBuilder()
      ..name = 'jenny'
      ..email = 'jenny@example.com'
      ..phone = (PhoneNumberBuilder()
            ..number = '415-555-0100'
            ..label = 'home')
          .build())
    .build();
```

在返回对象的函数中谨慎使用级联操作符。例如，下面的代码是错误的：

```dart
var sb = StringBuffer();
sb.write('foo')
  ..write('bar'); // 出错：void 对象中没有方法 write (Error: method 'write' isn't defined for 'void').
```

上述代码中的 `sb.write()` 方法返回的是 void，返回值为 `void` 的方法则不能使用级联运算符。

 **备忘:**

严格来说 `..` 级联操作并非一个运算符而是 Dart 的特殊语法。

### 其他运算符

大多数其它的运算符，已经在其它的示例中使用过：

| 运算符 | 名字         | 描述                                                         |
| ------ | ------------ | ------------------------------------------------------------ |
| `()`   | 使用方法     | 代表调用一个方法                                             |
| `[]`   | 访问 List    | 访问 List 中特定位置的元素                                   |
| `.`    | 访问成员     | 成员访问符                                                   |
| `?.`   | 条件访问成员 | 与上述成员访问符类似，但是左边的操作对象不能为 null，例如 foo?.bar，如果 foo 为 null 则返回 null ，否则返回 bar |

更多关于 `.`, `?.` 和 `..` 运算符介绍，请参考[类](https://dart.cn/guides/language/language-tour#classes).

