import matplotlib.pyplot as plt
import random

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def parse_history(history_str):
    valid_chars = [c for c in history_str if c in ('中', '歪')][-3:]
    state = {'pity': 0, 'consec_limited': 0, 'consec_standard': 0}
    for char in reversed(valid_chars):
        if char == '中':
            if state['consec_standard'] >= 2:
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
    current_state = {'pity': init_state['pity'], 'consec_limited': init_state['consec_limited'], 'consec_standard': init_state['consec_standard']}
    limited_count = 0
    for _ in range(pulls):
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
        hit = current_state['pity'] >= 79 or random.random() < 0.0075
        if hit:
            if random.random() < 0.5:
                limited_count += 1
                current_state['consec_limited'] += 1
                current_state['consec_standard'] = 0
            else:
                current_state['consec_standard'] += 1
                current_state['consec_limited'] = 0
            current_state['pity'] = 0
        else:
            current_state['pity'] += 1
        if (current_state['pity'] + 1) % 110 == 0:
            limited_count += 1
    return limited_count

def calculate_coin_exchange(total_pulls):
    return total_pulls // 110

def calculate_success_rate(pulls, target, coin_exchange, history_state):
    success = sum((simulate_gacha(pulls, history_state) + coin_exchange) >= target for _ in range(1000))
    return success / 1000

def recommend_target(total_pulls, target_star, coin_exchange, history_state):
    star_to_pulls = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
    if target_star in [2, 4]:
        return f"目标星级 {target_star} 星无效，推荐目标：3 星（需抽 4 把）"
    target_pulls = star_to_pulls[target_star]
    success_rate = calculate_success_rate(total_pulls, target_pulls, coin_exchange, history_state)
    if success_rate >= 0.5:
        return f"推荐目标：{target_star} 星（需抽 {target_pulls} 把，综合成功率：{success_rate * 100:.1f}%）"
    if target_star == 5:
        success_rate_3 = calculate_success_rate(total_pulls, star_to_pulls[3], coin_exchange, history_state)
        if success_rate_3 >= 0.5:
            return f"推荐目标：3 星（需抽 {star_to_pulls[3]} 把，综合成功率：{success_rate_3 * 100:.1f}%）"
        else:
            success_rate_1 = calculate_success_rate(total_pulls, star_to_pulls[1], coin_exchange, history_state)
            return f"推荐目标：1 星（需抽 {star_to_pulls[1]} 把，综合成功率：{success_rate_1 * 100:.1f}%）"
    elif target_star == 6:
        success_rate_5 = calculate_success_rate(total_pulls, star_to_pulls[5], coin_exchange, history_state)
        if success_rate_5 >= 0.5:
            return f"推荐目标：5 星（需抽 {star_to_pulls[5]} 把，综合成功率：{success_rate_5 * 100:.1f}%）"
        else:
            success_rate_3 = calculate_success_rate(total_pulls, star_to_pulls[3], coin_exchange, history_state)
            if success_rate_3 >= 0.5:
                return f"推荐目标：3 星（需抽 {star_to_pulls[3]} 把，综合成功率：{success_rate_3 * 100:.1f}%）"
            else:
                success_rate_1 = calculate_success_rate(total_pulls, star_to_pulls[1], coin_exchange, history_state)
                return f"推荐目标：1 星（需抽 {star_to_pulls[1]} 把，综合成功率：{success_rate_1 * 100:.1f}%）"
    return f"推荐目标：{target_star} 星（需抽 {target_pulls} 把，综合成功率：{success_rate * 100:.1f}%）"

def visualize_results(success_rate, target_star):
    plt.figure(figsize=(10, 6))
    colors = ['#6DD5FA', '#FF758C']
    wedges = plt.pie([success_rate, 1 - success_rate], labels=[f'达成{target_star}星', '未达成'], colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops={'linewidth': 2, 'edgecolor': 'white'}, textprops={'fontsize': 12, 'color': 'white'})
    if success_rate < 0.5:
        plt.text(0, -1.2, f"★ 幻塔抽卡建议：\n当前成功率较低，建议调整目标星级", ha='center', va='center', fontsize=10, bbox=dict(facecolor='#2C3E50', alpha=0.9, edgecolor='#3498DB'))
    plt.title(f"幻塔卡池模拟结果 - 目标{target_star}星当期限定", pad=20, fontsize=14, color='white')
    plt.gca().set_facecolor('#2C3E50')
    plt.show()

def main():
    plt.style.use('dark_background')
    while True:
        print("🌸 幻塔卡池模拟器 🌸")
        print("=" * 30)
        history = input("输入赤核抽卡的历史出货记录（中=限定，歪=常驻，例如'中歪中'）：").strip()
        plan_pulls = int(input("请输入你拥有的赤核数量："))
        target_star = int(input("当期限定需要抽到多少星："))
        history_state = parse_history(history)
        coin_exchange = calculate_coin_exchange(plan_pulls)
        recommendation = recommend_target(plan_pulls, target_star, coin_exchange, history_state)
        print("\n🔮 模拟结果分析：")
        print(f"- 铸币可兑换限定：{coin_exchange}个")
        print(f"- 预计新增限定：{simulate_gacha(plan_pulls, history_state)} ± 1个")
        print(recommendation)
        target_pulls = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}[target_star]
        success_rate = calculate_success_rate(plan_pulls, target_pulls, coin_exchange, history_state)
        print(f"- 综合成功率：{success_rate * 100:.1f}%")
        visualize_results(success_rate, target_star)
        if input("\n是否继续模拟？(y继续/其他退出)").lower() != 'y':
            print("感谢使用幻塔卡池模拟器！")
            break

if __name__ == "__main__":
    main()
