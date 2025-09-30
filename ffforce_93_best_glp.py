import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from matplotlib.widgets import TextBox, RadioButtons
import unicodedata

CSV_FILE = "openipf-2025-09-27-31932eca.csv"
df = pd.read_csv(CSV_FILE, low_memory=False)
df['WeightClassKg'] = df['WeightClassKg'].astype(str).str.replace(".0", "", regex=False)

def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFD', str(text).lower())
                   if unicodedata.category(c) != 'Mn')

categories = {
    'M': ['59', '66', '74', '83', '93', '105', '120+'],
    'F': ['47', '52', '57', '63', '72', '84', '84+']
}

current_sex = 'M'
current_cat = '93'
line = None
cat_radio = None
selected_athlete = None
athlete_info_text = None
error_text = None

fig, ax = plt.subplots(figsize=(10, 6))
fig.canvas.manager.set_window_title("Comparaison GLP - FFForce")
plt.subplots_adjust(left=0.25, right=0.75, top=0.95, bottom=0.25)

def get_best_df(sex, cat):
    subset = df[
        (df['Sex'] == sex) &
        (df['WeightClassKg'] == cat) &
        (df['Federation'] == 'FFForce')
    ].copy()
    best = subset.groupby('Name')['Goodlift'].max().reset_index()
    return best.sort_values(by='Goodlift', ascending=False).reset_index(drop=True)

def plot_distribution(best):
    global line, selected_athlete
    ax.clear()
    scores = best['Goodlift'].dropna().values
    if len(scores) == 0:
        ax.set_title(f"Aucune donnée pour {current_sex}, {current_cat}kg (FFForce)")
        fig.canvas.draw_idle()
        return

    mean, std = scores.mean(), scores.std()
    xmin, xmax = scores.min(), scores.max()
    x = pd.Series(range(int(xmin)-5, int(xmax)+5))
    y = stats.norm.pdf(x, mean, std)

    ax.hist(scores, bins=30, density=True, alpha=0.6, color='skyblue', label="Distribution des meilleurs GLP")
    ax.plot(x, y, 'r-', lw=2, label=f"Courbe gaussienne (μ={mean:.1f}, σ={std:.1f})")
    ax.set_title(f"Distribution GL Points ({current_sex}, {current_cat}kg, FFForce)")
    ax.set_xlabel("GL Points")
    ax.set_ylabel("Densité")
    ax.grid(alpha=0.3)
    ax.legend()

    # Réaffiche l’athlète sélectionné
    if selected_athlete is not None and not best.empty:
        score = selected_athlete['Goodlift']
        z_score = (score - mean) / std
        percentile = (scores <= score).sum() / len(scores) * 100
        line = ax.axvline(score, color='black', linestyle='--', lw=2)

        # Nouvelle annotation, toujours recréée
        ax.annotate(
            f"{selected_athlete['Name']}\n{score:.1f} GLP\nZ={z_score:.2f}\nP={percentile:.1f}%",
            xy=(score, 0), xycoords=('data', 'axes fraction'),
            xytext=(30, 50), textcoords='offset points',
            arrowprops=dict(arrowstyle="->", color="black"),
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.8),
            fontsize=9, ha='left'
        )

    fig.canvas.draw_idle()

axbox = plt.axes([0.25, 0.15, 0.5, 0.05])
text_box = TextBox(axbox, "Nom athlète : ")

def update_name(name):
    global selected_athlete, athlete_info_text, error_text
    best = get_best_df(current_sex, current_cat)
    scores = best['Goodlift'].dropna().values
    if len(scores) == 0:
        return

    mean, std = scores.mean(), scores.std()
    norm_name = normalize(name)
    matches = best[best['Name'].apply(lambda x: norm_name in normalize(x))]

    if athlete_info_text:
        athlete_info_text.set_text("")
    if error_text:
        error_text.set_text("")

    if not matches.empty:
        selected_athlete = matches.iloc[0]
        score = selected_athlete['Goodlift']
        rank = matches.index[0] + 1
        total = len(best)
        z_score = (score - mean) / std
        percentile = (scores <= score).sum() / len(scores) * 100

        info_str = (f"Nom : {selected_athlete['Name']} | GLP : {score:.1f} | "
                    f"Rang : {rank}/{total} | Z : {z_score:.2f} | Percentile : {percentile:.1f}%")
        if athlete_info_text is None:
            athlete_info_text = fig.text(0.25, 0.12, info_str, fontsize=10, color='blue', ha='left')
        else:
            athlete_info_text.set_text(info_str)
        plot_distribution(best)
    else:
        selected_athlete = None
        msg = f"Athlète '{name}' introuvable dans {current_sex}, {current_cat}kg."
        if error_text is None:
            error_text = fig.text(0.25, 0.12, msg, fontsize=10, color='red', ha='left')
        else:
            error_text.set_text(msg)
        fig.canvas.draw_idle()

text_box.on_submit(update_name)

ax_sex = plt.axes([0.05, 0.5, 0.15, 0.2], facecolor='lightgoldenrodyellow')
sex_radio = RadioButtons(ax_sex, ['Homme', 'Femme'], active=0)

def on_sex_change(label):
    global current_sex, current_cat, cat_radio, selected_athlete
    current_sex = 'M' if label == 'Homme' else 'F'
    current_cat = categories[current_sex][0]
    selected_athlete = None

    cat_radio.ax.clear()
    cat_radio = RadioButtons(cat_radio.ax, categories[current_sex], active=0)
    cat_radio.on_clicked(on_cat_change)
    plot_distribution(get_best_df(current_sex, current_cat))

sex_radio.on_clicked(on_sex_change)

ax_cat = plt.axes([0.8, 0.3, 0.15, 0.6], facecolor='lightyellow')
cat_radio = RadioButtons(ax_cat, categories[current_sex], active=categories[current_sex].index(current_cat))

def on_cat_change(label):
    global current_cat, selected_athlete
    current_cat = label
    selected_athlete = None
    plot_distribution(get_best_df(current_sex, current_cat))

cat_radio.on_clicked(on_cat_change)

plot_distribution(get_best_df(current_sex, current_cat))
plt.show()
