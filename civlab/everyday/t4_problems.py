"""T4 · Answer ensembles (plan v2.1 §8.5). 48 generated multi-step problems with computed integer answers:
16 easy, 16 medium, 16 hard. Deterministic (seed "t4-v1"); none reuse the v1 demo items.
Each template returns (question, answer) and only emits instances with an integer answer."""
import math, random

def e_shop(r):
    a, b, c = r.randint(3, 9), r.randint(2, 6), r.randint(4, 12)
    pa, pb = r.randint(2, 9), r.randint(5, 15)
    return (f"A customer buys {a} notebooks at ${pa} each and {b} packs of pens at ${pb} per pack, and pays with a ${a*pa+b*pb+c} bill. "
            f"How many dollars of change do they get?", c)
def e_discount(r):
    p = r.choice([40, 60, 80, 120, 150, 200, 250]); d = r.choice([10, 20, 25, 30, 50])
    return (f"A jacket costs ${p}. It is discounted by {d}%. What is the sale price in dollars?", p * (100 - d) // 100) if p * d % 100 == 0 else None
def e_rate(r):
    s, h = r.randint(30, 90), r.randint(2, 6)
    return (f"A train travels at {s} km per hour for {h} hours and then stops. How many kilometres did it travel?", s * h)
def e_share(r):
    k = r.randint(3, 8); each = r.randint(4, 15); left = r.randint(1, k - 1)
    return (f"{k*each+left} stickers are shared equally among {k} children, and the leftover stickers are kept by the teacher. "
            f"How many stickers does the teacher keep?", left)
def e_age(r):
    a, d = r.randint(8, 20), r.randint(3, 12)
    return (f"Maya is {a} years old. Her brother is {d} years older. In 5 years, what will be the sum of their ages?", a + a + d + 10)

def m_work(r):
    a, b = r.choice([(6, 3), (12, 4), (10, 15), (20, 30), (12, 6), (8, 24)])
    t = a * b / (a + b)
    return (f"Pipe A fills a tank in {a} hours and pipe B fills it in {b} hours. With both open, how many hours to fill it?", int(t)) if t == int(t) else None
def m_mix(r):
    x, y = r.randint(2, 8) * 10, r.randint(2, 8) * 10; px, py = r.choice([10, 20, 30]), r.choice([40, 50, 60])
    tot = (x * px + y * py) / 100
    return (f"You mix {x} litres of {px}% juice with {y} litres of {py}% juice. How many litres of pure juice are in the mixture?", int(tot)) if tot == int(tot) else None
def m_tax(r):
    h, w, t = r.randint(20, 40), r.choice([15, 18, 20, 25]), r.choice([10, 20, 25])
    g = h * w
    return (f"A worker earns ${w} per hour and works {h} hours. After {t}% tax, how many dollars does she keep?", g * (100 - t) // 100) if g * t % 100 == 0 else None
def m_speed(r):
    d = r.choice([60, 120, 180, 240]); v1, v2 = r.choice([(20, 30), (30, 60), (40, 60), (20, 60)])
    t = d / v1 + d / v2; avg = 2 * d / t
    return (f"A cyclist rides {d} km at {v1} km/h and returns the same way at {v2} km/h. What is the average speed for the round trip in km/h?", int(avg)) if avg == int(avg) else None
def m_percent_chain(r):
    p = r.choice([100, 200, 400, 500, 800]); up, down = r.choice([(20, 25), (25, 20), (50, 20), (10, 10)])
    v = p * (100 + up) / 100 * (100 - down) / 100
    return (f"A price of ${p} rises by {up}% and then falls by {down}%. What is the final price in dollars?", int(v)) if v == int(v) else None
def m_legs(r):
    c, k = r.randint(5, 20), r.randint(5, 20)
    return (f"A farm has chickens and cows with {c+k} heads and {2*c+4*k} legs in total. How many cows are there?", k)

def h_crt(r):
    a, b = r.choice([(3, 5), (4, 7), (5, 7), (3, 8)]); ra, rb = r.randint(1, a - 1), r.randint(1, b - 1); lo = r.randint(20, 60)
    n = next(x for x in range(lo + 1, lo + 1 + a * b * 2) if x % a == ra and x % b == rb)
    return (f"What is the smallest number greater than {lo} that leaves remainder {ra} when divided by {a} and remainder {rb} when divided by {b}?", n)
def h_comb(r):
    n, k = r.randint(5, 9), r.choice([2, 3])
    return (f"A committee of {k} people is chosen from {n} candidates, and one specific candidate refuses to serve with another specific candidate. "
            f"How many different committees are possible?", math.comb(n, k) - math.comb(n - 2, k - 2))
def h_age2(r):
    k, y = r.choice([2, 3]), r.randint(4, 10); m = r.choice([2, 3, 4])
    # parent = k*child now; y years ago parent = (k+m-? ) solve integer: parent - y = q*(child - y)
    for child in range(y + 1, 40):
        p = k * child
        for q in range(k + 1, 8):
            if p - y == q * (child - y):
                return (f"A parent is {k} times as old as their child. {y} years ago the parent was {q} times as old as the child. How old is the parent now?", p)
    return None
def h_stairs(r):
    n = r.randint(6, 12); f = [1, 1]
    for _ in range(n): f.append(f[-1] + f[-2])
    return (f"You climb a staircase of {n} steps taking 1 or 2 steps at a time. How many distinct ways can you reach the top?", f[n])
def h_digits(r):
    t = r.randint(4, 9)
    cnt = sum(1 for hh in range(24) for mm in range(60) if sum(map(int, f"{hh:02d}{mm:02d}")) == t)
    return (f"A 24-hour digital clock shows HH:MM. In one full day, how many different times have digits that add up to exactly {t}?", cnt)

TEMPLATES = {"easy": [e_shop, e_discount, e_rate, e_share, e_age],
             "medium": [m_work, m_mix, m_tax, m_speed, m_percent_chain, m_legs],
             "hard": [h_crt, h_comb, h_age2, h_stairs, h_digits]}

def problems(seed="t4-v1", per_level=16):
    r = random.Random(seed); out = []; seen = set()
    for level, tmpls in TEMPLATES.items():
        k = 0; i = 0
        while k < per_level:
            got = tmpls[i % len(tmpls)](r); i += 1
            if not got or got[0] in seen: continue
            seen.add(got[0]); k += 1
            out.append({"pid": f"{level[0]}{k:02d}", "level": level, "q": got[0], "answer": int(got[1])})
    return out

SYSTEM = "You solve short quantitative word problems. Show brief working, then give the answer."
def build_prompt(q):
    return q + "\n\nShow brief working (a few lines at most). End with a line in exactly this format:\nANSWER: <a single integer>"
