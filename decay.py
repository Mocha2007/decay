from json import load
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from copy import deepcopy
from random import choice, seed

plt.rcParams.update({'font.size': 8})

isotope_data = load(open('isotopes.json', 'r', encoding='utf-8'))
colors = [ # from matplotlib.colors import cnames
	'red',
	'orange',
	'yellow',
	'green',
	'blue',
	'purple',
	'pink',
	'brown',
	'grey',
	'black',
]
units = {
	'd': 24 * 60 * 60,
	'h': 60 * 60,
	'min': 60,
	's': 1,
	'yr': 365.2425 * 24 * 60 * 60,
}


def decay(isotope_counts: dict, t: float=1):
	"""t in s"""
	out = deepcopy(isotope_counts)
	for i, fraction in isotope_counts.items():
		try:
			isotope = Isotope(i, isotope_data[i])
		except KeyError:
			continue # non-radioactive
		# get decay volume
		decay_volume = isotope.decay_chance(t) * fraction
		# delete decay from parent
		out[i] -= decay_volume
		# add proportionally to daughters
		for daughter, chance in isotope.daughters.items():
			daughter_volume = decay_volume * chance
			if daughter in out:
				out[daughter] += daughter_volume
			else:
				out[daughter] = daughter_volume
	return out


def time2num(val: float, unit: str) -> float:
	return val * units[unit]


class Isotope:
	def __init__(self, name: str, data: dict):
		self.name = name
		self.daughters = data['daughters']
		self.halflife = time2num(*data['half-life'])

	def __eq__(self, other) -> bool:
		return self.name == other.name

	def decay_chance(self, t: float) -> float:
		return 1 - 2 ** (-t / self.halflife)


# PLOTTING

fig = plt.figure()
print('Begin Plot')

# PLOT 1
plot1 = fig.add_subplot(1, 1, 1)
# SERIES
# C14, U238, Pu244
seeds = {
	'Pu244': 1
}
duration = units['yr'] * 1e9 # 1 byr
divisions = 1000
step_size = duration/divisions
record = {}
for step in range(divisions):
	# record data
	x = step * step_size
	for isotope, y in seeds.items():
		if isotope in record:
			record[isotope].append((x, y))
		else:
			record[isotope] = [(x, y)]
	# simulate decay
	seeds = decay(seeds, step_size)
# plot data
isotope_colors = {}
for isotope, points in record.items():
	x, y = zip(*points)
	print(isotope, type(isotope))
	seed(isotope)
	color = choice(colors)
	plt.plot(x, y, color=color)
	isotope_colors[isotope] = color

plt.xlabel('Time (s)')
plt.ylabel('Fraction')
plt.title('Isotopic Fractions over Time')
# legend
plt.legend(handles=[
	Patch(color=color, label=isotope)
for isotope, color in isotope_colors.items()])

plt.show()