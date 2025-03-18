import matplotlib.pyplot as plt
import random


def parse_history(history_str):
    """仅解析最近3次抽卡记录"""
    # 只取最后3个有效字符
    valid_chars = [c for c in history_str if c in ('中', '歪')][-3:]
    pity = 0
    consec_limited = 0
    consec_standard = 0

    # 逆向解析，从最新记录向历史追溯
    for char in reversed(valid_chars):
        if char == '中':
            if consec_standard >= 2:
                # 触发强制转换后重置
                consec_limited = 1
                consec_standard = 0
            else:
                consec_limited += 1
                consec_standard = 0
            pity = 0
        elif char == '歪':
            if consec_limited >= 2:
                consec_standard = 1
                consec_limited = 0
            else:
                consec_standard += 1
                consec_limited = 0
            pity = 0
    return pity, consec_limited, consec_standard


def simulate_gacha(pulls, init_pity=0, init_consec_limited=0, init_consec_standard=0):
    """
    抽卡模拟核心逻辑
    :param pulls: 计划抽取次数
    :param init_pity: 初始保底进度
    :param init_consec_limited: 初始连续当期限定次数
    :param init_consec_standard: 初始连续常驻次数
    """
    pity_counter = init_pity
    limited_count = 0
    standard_count = 0
    consec_limited = init_consec_limited
    consec_standard = init_consec_standard

    for _ in range(pulls):
        # 强制转换规则（优先级最高）
        if consec_standard >= 2:
            # 连续2次未出限定，强制出当期限定
            limited_count += 1
            consec_limited = 1
            consec_standard = 0
            pity_counter = 0
            continue
        elif consec_limited >= 2:
            # 连续2次出限定，强制出常驻
            standard_count += 1
            consec_standard = 1
            consec_limited = 0
            pity_counter = 0
            continue

        # 保底检测（80抽保底）
        hit = pity_counter >= 79
        if not hit:
            hit = random.random() < 0.0075  # 基础概率0.75%

        if hit:
            # 出货类型判断
            if random.random() < 0.5:  # 50%概率出当期限定
                limited_count += 1
                consec_limited = consec_limited + 1 if consec_limited > 0 else 1
                consec_standard = 0
            else:
                standard_count += 1
                consec_standard = consec_standard + 1 if consec_standard > 0 else 1
                consec_limited = 0
            pity_counter = 0
        else:
            pity_counter += 1

    return limited_count


def main():
    plt.rcParams['font.sans-serif'] = ['SimHei']

    while True:
        # 用户输入
        history = input("请输入历史记录(中=当期限定，歪=常驻，空=无记录 最多输入3个)：").strip()
        plan_pulls = int(input("请输入计划抽取次数："))
        target = int(input("需要抽到多少個当期限定："))

        # 解析历史记录
        init_pity, init_cl, init_cs = parse_history(history)
        history_limited = history.count('中')

        # 模拟100次
        success = 0
        for _ in range(100):
            new_limited = simulate_gacha(plan_pulls, init_pity, init_cl, init_cs)
            if (history_limited + new_limited) >= target:
                success += 1

        # 可视化
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # 饼图
        ax1.pie([success, 100 - success],
                labels=[f'达成目标', '未达成'],
                colors=['#4CAF50', '#F44336'],
                autopct='%1.1f%%')
        ax1.set_title(f"当期限定抽中{target}个的概率")

        # 数据表格
        ax2.axis('off')
        table_data = [
            ["历史当期限定数", history_limited],
            ["后续计划抽数", plan_pulls],
            ["目标达成次数", success],
            ["综合成功率", f"{success}%"]
        ]
        ax2.table(cellText=table_data,
                  colLabels=None,
                  cellLoc='center',
                  loc='center')

        plt.suptitle("限定卡池模拟报告", fontsize=14)
        plt.show()

        if input("是否继续模拟？(y继续/其他退出)").lower() != 'y':
            break


if __name__ == "__main__":
    main()