import matplotlib.pyplot as plt
import random

def simulate_gacha(pulls):
    pity_counter = 0  # 保底计数器
    a, b = 0, 0  # A和B的数量
    consecutive_a = 0  # 连续A的计数器
    consecutive_non_a = 0  # 未出A的计数器
    log = []  # 记录出货日志
    extra_a_counter = 0  # 每110抽额外增加一个A的计数器

    for pull in range(1, pulls + 1):
        # 每110抽额外增加一个A
        if pull % 110 == 0:
            a += 1
            log.append(f"Extra A at {pull}")

        # 保底检测
        hit = pity_counter >= 79
        if not hit:
            hit = random.random() < 0.0075  # 基础概率0.75%

        if hit:
            # 强制转换逻辑
            if consecutive_a >= 2 or consecutive_non_a >= 2:
                current = 'B'
                consecutive_a = 0
                consecutive_non_a = 0
            else:
                current = 'A' if random.random() < 0.5 else 'B'
                consecutive_a = (consecutive_a + 1) if current == 'A' else 0
                consecutive_non_a = (consecutive_non_a + 1) if current == 'B' else 0

            a += 1 if current == 'A' else 0
            b += 1 if current == 'B' else 0
            log.append(pull)
            pity_counter = 0
        else:
            pity_counter += 1

    return a, b, log

def main():
    while True:
        # 输入抽取次数
        pulls = int(input("请输入抽取次数（例如350）："))
        # 输入自定义n值
        n = int(input("请输入自定义n值（例如3）："))

        # 运行100次模拟
        results = [simulate_gacha(pulls)[0] for _ in range(100)]

        # 每10次统计一次概率
        probabilities = []
        for i in range(10, 101, 10):
            subset = results[:i]
            count_n_a_or_more = sum(1 for x in subset if x >= n)
            probability_n_a_or_more = count_n_a_or_more / i
            probabilities.append(probability_n_a_or_more)
            print(f"前{i}次模拟中，{pulls}抽出{n}个及以上A的概率：{probability_n_a_or_more * 100:.2f}%")

        # 统计100次中出n个及以上A的次数
        count_n_a_or_more = sum(1 for x in results if x >= n)
        probability_n_a_or_more = count_n_a_or_more / 100

        # 数据准备
        labels = [f'{n}个及以上A', '其他']
        sizes = [count_n_a_or_more, 100 - count_n_a_or_more]
        colors = ['#FF6B6B', '#4ECDC4']

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        # 绘制饼图
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, wedgeprops={'width':0.6, 'edgecolor':'white'})
        ax1.axis('equal')
        plt.title(f"{pulls}抽出{n}个及以上A的概率")
        plt.show()

        # 绘制表格
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.axis('off')
        table_data = [
            ["抽取次数", pulls],
            ["自定义n值", n],
            [f"100次模拟中{n}个及以上A的次数", count_n_a_or_more],
            [f"{n}个及以上A的概率", f"{probability_n_a_or_more * 100:.2f}%"]
        ]
        table = ax2.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.4, 0.4])
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)
        plt.title("统计结果")
        plt.show()

        # 输出最终结果
        print(f"100次模拟中，{pulls}抽出{n}个及以上A的次数：{count_n_a_or_more}")
        print(f"{pulls}抽出{n}个及以上A的概率：{probability_n_a_or_more * 100:.2f}%")

        # 问询是否继续
        continue_input = input("是否继续模拟？(输入 'y' 继续，其他退出)：")
        if continue_input.lower() != 'y':
            print("程序已退出。")
            break

if __name__ == "__main__":
    main()