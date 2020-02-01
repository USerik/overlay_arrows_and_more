# -*- coding: utf-8 -*-

import win32api
import win32con
import win32gui
import win32ui

from threading import Thread

from enum import Enum


class Shape(Enum):
	rectangle = 0
	ellipse = 1
	arrow = 2


class TransparentWindow(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.h_window = None

	def run(self):
		h_instance = win32api.GetModuleHandle()
		class_name = 'MyWindowClassName'
		wnd_class = win32gui.WNDCLASS()

		wnd_class.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
		wnd_class.lpfnWndProc = wnd_proc
		wnd_class.hInstance = h_instance
		wnd_class.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
		wnd_class.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
		wnd_class.lpszClassName = class_name

		wnd_class_atom = win32gui.RegisterClass(wnd_class)
		ex_style = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | \
				   win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
		style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE

		self.h_window = win32gui.CreateWindowEx(
			ex_style, wnd_class_atom,
			'OverlayWindow',  # WindowName
			style,
			0,  # x
			0,  # y
			win32api.GetSystemMetrics(win32con.SM_CXSCREEN),  # width
			win32api.GetSystemMetrics(win32con.SM_CYSCREEN),  # height
			None,  # hWndParent
			None,  # hMenu
			h_instance,
			None  # lpParam
		)

		win32gui.SetLayeredWindowAttributes(self.h_window, 0x00ffffff, 128, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)
		win32gui.SetWindowPos(self.h_window, win32con.HWND_TOPMOST, 0, 0, 0, 0,
							  win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

		win32gui.PumpMessages()

	def refresh(self):
		win32gui.InvalidateRect(self.h_window, None, True)


graphical_elements = []

def add(**geometry):
	global graphical_elements
	graphical_elements.append(geometry)

def wnd_proc(h_wnd, message, w_param, l_param):
	"""Displays a transparent window with some graphic elements

	Displays a transparent window with some graphic elements

	:param h_wnd: an input argument

	:returns: nothing
	"""
	global graphical_elements
	if message == win32con.WM_PAINT:
		hdc, paint_struct = win32gui.BeginPaint(h_wnd)
		win32gui.BringWindowToTop(h_wnd)

		for r in graphical_elements:

			if 'color' in r:
				color_r = r['color'][0]
				color_g = r['color'][1]
				color_b = r['color'][2]
			else:
				color_r = 255
				color_g = 0
				color_b = 0

			if 'thickness' in r:
				thickness = r['thickness']
			else:
				thickness = 5

			pen = win32gui.CreatePen(win32con.PS_GEOMETRIC, thickness, win32api.RGB(color_r, color_g, color_b))
			win32gui.SelectObject(hdc, pen)

			if r['geometry'] is Shape.rectangle:
				win32gui.Rectangle(hdc, r['x'], r['y'], r['x'] + r['width'], r['y'] + r['height'])

				brush = win32gui.CreateHatchBrush(win32con.HS_DIAGCROSS, win32api.RGB(0, 0, 255))
				win32gui.SelectObject(hdc, brush)

				win32gui.ExtFloodFill(hdc, r['x']+ r['width']/2, r['y']+ r['height']/2, win32api.RGB(color_r, color_g, color_b), win32con.FLOODFILLBORDER)
			elif r['geometry'] is Shape.ellipse:
				win32gui.Ellipse(hdc, r['x'], r['y'], r['width'], r['height'])
			else:
				print('Unknown geometry of graphical element: ' + r)


		win32gui.EndPaint(h_wnd, paint_struct)
		return 0

	# elif message == win32con.WM_DESTROY:
	#	print 'Closing the window.'
	#	win32gui.PostQuitMessage(0)
	#	return 0
	else:
		return win32gui.DefWindowProc(h_wnd, message, w_param, l_param)


if __name__ == '__main__':
	transparent_window = TransparentWindow()
	transparent_window.start()
	add(geometry=Shape.ellipse, x=10, y=10, width=40, height=40)
	add(geometry=Shape.rectangle, x=100, y=100, width=100, height=100, color=(0, 0, 255))
	add(geometry=Shape.rectangle, x=300, y=100, width=100, height=100, thickness=10, color=(0, 255, 0))
	transparent_window.refresh()
