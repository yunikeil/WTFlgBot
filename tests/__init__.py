import os
import asyncio


current_dir = os.path.abspath(os.path.dirname(__file__))

#sys.path.insert(0, current_dir)
#sys.path.insert(0, os.path.join(current_dir, "..", "cogs"))
#sys.path.insert(0, os.path.join(current_dir, "..", "data"))

test_modules = [
    __import__(f[:-3]) for f in os.listdir(current_dir) if f.endswith("_test.py")
]


async def start_all(**kwargs):
    results = {}

    for test_module in test_modules:
        if all(
            [  # debugging
                "ast" not in test_module.__name__,
                "dbw" not in test_module.__name__,
                "srv" not in test_module.__name__,
            ]
        ):
            pass  # continue

        results[test_module.__name__] = await test_module.run_tests(**kwargs)
        info_str = results[test_module.__name__][0], test_module, type(test_module)

        if kwargs.get("autosend"):
            await kwargs.get("thread").send(results[test_module.__name__][1])
        result = f"```{test_module.__name__} => {info_str}```"
        await kwargs.get("thread").send(result)

    return results


if __name__ == "__main__":
    asyncio.run(start_all())
