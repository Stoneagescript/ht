import matplotlib.pyplot as plt
import random

plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows系统常用字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题


def parse_history(history_str):
    """幻塔专属历史记录解析（仅处理最近3次有效记录）"""
    valid_chars = [c for c in history_str if c in ('中', '歪')][-3:]  # 只取最近3次
    state = {
        'pity': 0,  # 保底进度
        'consec_limited': 0,  # 连续限定次数
        'consec_standard': 0  # 连续常驻次数
    }

    # 逆向解析最新状态
    for char in reversed(valid_chars):
        if char == '中':
            if state['consec_standard'] >= 2:
                # 触发强制转换后重置
                state['consec_limited'] = 1
                state['consec_standard'] = 0
            else:
                state['consec_limited'] += 1
                state['consec_standard'] = 0
            state['pity'] = 0
        elif char == '歪':
            if state['consec_limited'] >= 2:
                state['consec_standard'] = 1
                state['consec_limited'] = 0
            else:
                state['consec_standard'] += 1
                state['consec_limited'] = 0
            state['pity'] = 0
    return state


def simulate_gacha(pulls, init_state):
    """幻塔专属抽卡模拟引擎"""
    current_state = {
        'pity': init_state['pity'],
        'consec_limited': init_state['consec_limited'],
        'consec_standard': init_state['consec_standard']
    }
    limited_count = 0

    for _ in range(pulls):
        # 幻塔强制转换规则
        if current_state['consec_standard'] >= 2:
            limited_count += 1
            current_state['consec_limited'] = 1
            current_state['consec_standard'] = 0
            current_state['pity'] = 0
            continue
        if current_state['consec_limited'] >= 2:
            current_state['consec_standard'] = 1
            current_state['consec_limited'] = 0
            current_state['pity'] = 0
            continue

        # 保底机制（幻塔80抽保底）
        hit = current_state['pity'] >= 79
        if not hit:
            hit = random.random() < 0.0075  # 幻塔基础概率0.75%

        if hit:
            if random.random() < 0.5:  # 幻塔50%UP概率
                limited_count += 1
                current_state['consec_limited'] += 1
                current_state['consec_standard'] = 0
            else:
                current_state['consec_standard'] += 1
                current_state['consec_limited'] = 0
            current_state['pity'] = 0
        else:
            current_state['pity'] += 1

        # 幻塔特殊机制：每110抽额外奖励
        if (current_state['pity'] + 1) % 110 == 0:
            limited_count += 1

    return limited_count


def calculate_coin_exchange(total_pulls):
    """计算铸币可兑换的限定数量"""
    coins = total_pulls  # 每抽获得1个铸币
    return coins // 110  # 每110铸币兑换1个


def recommend_target_with_coins(total_pulls, target, coin_exchange):
    """根据铸币兑换数量推荐目标"""
    adjusted_target = max(0, target - coin_exchange)  # 实际需要抽取的数量
    if adjusted_target == 0:
        return "铸币已足够兑换目标数量，无需额外抽取"

    # 计算不同目标的综合概率
    recommendations = []
    for t in range(max(1, adjusted_target - 1), adjusted_target + 1):  # 推荐更少的星数
        success = 0
        for _ in range(1000):
            new_limited = simulate_gacha(total_pulls, {'pity': 0, 'consec_limited': 0, 'consec_standard': 0})
            if new_limited >= t:  # 仅计算通过抽卡和额外奖励获得的限定数量
                success += 1
        probability = success / 1000
        recommendations.append((t, probability))

    # 生成推荐信息
    result = "推荐方案：\n"
    for t, prob in recommendations:
        result += f"- 目标{t}个（综合成功率：{prob * 100:.1f}%）\n"
    return result


def visualize_results(success_rate, target):
    """幻塔风格可视化"""
    plt.figure(figsize=(10, 6))

    # 渐变色饼图
    colors = ['#6DD5FA', '#FF758C']  # 幻塔主题色
    wedges = plt.pie(
        [success_rate, 1 - success_rate],
        labels=[f'达成{target}个', '未达成'],
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'linewidth': 2, 'edgecolor': 'white'},
        textprops={'fontsize': 12, 'color': 'white'}
    )

    # 添加概率提示
    if success_rate < 0.5:
        plt.text(0, -1.2,
                 f"★ 幻塔抽卡建议：\n当前成功率较低，建议：\n- 目标调整为{target - 1}个（成功率>50%）\n- 或等待概率UP活动",
                 ha='center', va='center', fontsize=10,
                 bbox=dict(facecolor='#2C3E50', alpha=0.9, edgecolor='#3498DB'))

    plt.title(f"幻塔卡池模拟结果 - 目标{target}个当期限定", pad=20, fontsize=14, color='white')
    plt.gca().set_facecolor('#2C3E50')  # 幻塔深空背景色
    plt.show()


def main():
    plt.style.use('dark_background')  # 暗黑模式

    while True:
        # 幻塔风格用户界面
        print("🌸 幻塔卡池模拟器 🌸")
        print("=" * 30)
        history = input("输入历史记录（中=限定，歪=常驻，例如'中歪中'）：").strip()
        plan_pulls = int(input("请输入计划抽取次数："))
        target = int(input("需要抽到多少個当期限定："))

        # 解析历史状态（仅用于初始化，不计入当前卡池的限定数量）
        history_state = parse_history(history)

        # 计算铸币兑换数量
        total_pulls = plan_pulls  # 假设历史铸币已用完
        coin_exchange = calculate_coin_exchange(total_pulls)
        adjusted_target = max(0, target - coin_exchange)

        # 蒙特卡洛模拟（1000次提高精度）
        success = 0
        for _ in range(1000):
            new_limited = simulate_gacha(plan_pulls, history_state)
            if (new_limited + coin_exchange) >= target:  # 仅计算当前卡池的限定数量
                success += 1

        # 生成推荐方案
        recommendations = recommend_target_with_coins(plan_pulls, target, coin_exchange)

        # 输出结果
        print("\n🔮 模拟结果分析：")
        print(f"- 铸币可兑换限定：{coin_exchange}个")
        print(f"- 预计新增限定：{simulate_gacha(plan_pulls, history_state)} ± 1个")
        print(f"- 综合成功率：{success / 1000 * 100:.1f}%")
        print(recommendations)

        # 可视化展示
        visualize_results(success / 1000, target)

        if input("\n是否继续模拟？(y继续/其他退出)").lower() != 'y':
            print("感谢使用幻塔卡池模拟器！")
            break


if __name__ == "__main__":
    main()
