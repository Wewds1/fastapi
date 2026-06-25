# import asyncio
#
# async def main():
#     task = asyncio.create_task(other_function())
#     print("A")
#     await asyncio.sleep(1)
#     print("b")
#     await task
#
# async def other_function():
#     print("1")
#     print("2")
#
#
# asyncio.run(main())



# x = [1, 2, 3]
#
# y = x.copy()
#
# y.append(4)
#
# print(x)
# print(y)


def func(a=[]):
    a.append(1)
    return a


def func1(a=None):
    if a is None:
        a = []
    a.append(1)
    return a