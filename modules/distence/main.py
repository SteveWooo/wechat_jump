import cv2;
import numpy as np
import os, glob, shutil
import random

def multi_scale_search(pivot, screen, range=0.3, num=10):
    H, W = screen.shape[:2]
    h, w = pivot.shape[:2]

    found = None
    for scale in np.linspace(1-range, 1+range, num)[::-1]:
        resized = cv2.resize(screen, (int(W * scale), int(H * scale)))
        r = W / float(resized.shape[1])
        if resized.shape[0] < h or resized.shape[1] < w:
            break
        res = cv2.matchTemplate(resized, pivot, cv2.TM_CCOEFF_NORMED)

        loc = np.where(res >= res.max())
        pos_h, pos_w = list(zip(*loc))[0]

        if found is None or res.max() > found[-1]:
            found = (pos_h, pos_w, r, res.max())

    if found is None: return (0,0,0,0,0)
    pos_h, pos_w, r, score = found
    start_h, start_w = int(pos_h * r), int(pos_w * r)
    end_h, end_w = int((pos_h + h) * r), int((pos_w + w) * r)
    return [start_h, start_w, end_h, end_w, score]

class wechat_jump(object):
	def __init__(self):
		self.resource_dir = "./resources"
		self.sensitivity = 2.045
		self.bb_size = [300, 300]
		self.load_resources()
		
	def load_resources(self):
		self.player = cv2.imread(os.path.join(self.resource_dir + '/position/player.png'), 0)
		circle_file = glob.glob(os.path.join(self.resource_dir + '/position/circle/*.png'))
		table_file  = glob.glob(os.path.join(self.resource_dir + '/position/table/*.png'))
		self.jump_file = [cv2.imread(name, 0) for name in circle_file + table_file]

	def get_player_position(self, state):
		state = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY)
		pos = multi_scale_search(self.player, state, 0.3, 10)
		h, w = int((pos[0] + 13 * pos[2])/14.), (pos[1] + pos[3])//2
		return np.array([h, w])

	def get_target_position_fast(self, state, player_pos):
		state_cut = state[:player_pos[0],:,:]
		m1 = (state_cut[:, :, 0] == 245)
		m2 = (state_cut[:, :, 1] == 245)
		m3 = (state_cut[:, :, 2] == 245)
		m = np.uint8(np.float32(m1 * m2 * m3) * 255)
		b1, b2 = cv2.connectedComponents(m)
		for i in range(1, np.max(b2) + 1):
			x, y = np.where(b2 == i)
			# print('fast', len(x))
			if len(x) > 280 and len(x) < 310:
				r_x = []
				r_y = x, y
		h, w = int(r_x.mean()), int(r_y.mean())
		return np.array([h, w])

	def get_target_position(self, state, player_pos):
		state = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY)
		sym_center = [1280, 720] - player_pos
		sym_tl = np.maximum([0,0], sym_center + np.array([-self.bb_size[0]//2, -self.bb_size[1]//2]))
		sym_br = np.array([min(sym_center[0] + self.bb_size[0]//2, player_pos[0]), min(sym_center[0] + self.bb_size[1]//2, 720)])
		state_cut = state[sym_tl[0]:sym_br[0], sym_tl[1]:sym_br[1]]
		target_pos = None
		for target in self.jump_file:
			pos = multi_scale_search(target, state_cut, 0.4, 15)
			if target_pos is None or pos[-1] > target_pos[-1]:
				target_pos = pos
		return np.array([(target_pos[0]+target_pos[2])//2, (target_pos[1]+target_pos[3])//2]) + sym_tl

	def get_state(self):
		# state image
		# os.system('adb shell screencap -p /sdcard/state.png')
		# os.system('adb pull /sdcard/state.png ' + self.resource_dir + '/screen/state.png')
		state = cv2.imread(self.resource_dir + '/screen/state.png')
		self.resolution = state.shape[:2]
		scale = state.shape[1] / 720.0
		state = cv2.resize(state, (720, int(state.shape[0] / scale)), interpolation=cv2.INTER_NEAREST)
		if state.shape[0] > 1280:
			s = state.shape[0] - 1280
			state = state[s:,:,:]
		elif state.shape[0] < 1280:
			s = 1280 - state.shape[0]
			state = np.concatenate((255 * np.ones((s, 720, 3), dtype=np.uint8), state), 0)
		return state

	def jump(self, player_pos, target_pos):
		distance = np.linalg.norm(player_pos - target_pos)
		press_time = distance * self.sensitivity
		press_time = int(press_time)
		press_h, press_w = random.randint(300,800), random.randint(200,800)
		cmd = 'adb shell input swipe {} {} {} {} {}'.format(press_w, press_h, press_w, press_h, press_time)
		print(cmd)
		os.system(cmd)

	def run(self):
		self.state = self.get_state()
		self.player_pos = self.get_player_position(self.state)
		try:
			self.target_pos = self.get_target_position_fast(self.state, self.player_pos)
		except:
			self.target_pos = self.get_target_position(self.state, self.player_pos)
		self.jump(self.player_pos, self.target_pos);

if __name__ == "__main__":
	wj = wechat_jump()
	wj.run()