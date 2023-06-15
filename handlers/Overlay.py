import threading

import mediapipe as mp

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
mpl.rcParams['toolbar'] = 'None'
mpl.rcParams['backend'] = 'TkAgg'


class Overlay:

    def __init__(self, video_processor_instance):
        self._video_processor = video_processor_instance

        self.on = False
        self.scale = 1
        self.opacity = 0.5
        self._current_scale = self.scale

        self._hand_visualization_thread = threading.Thread(target=self._hand_visualization, daemon=True)
        self._hand_visualization_thread.start()

    
    def toggle(self):
        self.on = not self.on


    def _hand_visualization(self):
        def _update_data(_):
            if self.on:
                fm.window.attributes('-alpha', self.opacity)
                if self.scale != self._current_scale:
                    fig.set_dpi(100*self.scale)
                    self._current_scale = self.scale

            elif not self.on:
                fm.window.attributes('-alpha', 0)
                plot, = ax.plot3D([0], [0], [0], color='red', linewidth=1)
                return plot,

            fm.window.attributes("-topmost", True)
            try:
                with self._video_processor.hand_detection_lock:
                    landmark_list = self._video_processor.hand_detection_results.multi_hand_landmarks[0]
                connections = mp_hands.HAND_CONNECTIONS

            except:
                plot, = ax.plot3D([0], [0], [0], color='red', linewidth=1)
                return plot, 
        
            plotted_landmarks = {}

            for idx, landmark in enumerate(landmark_list.landmark):
                if ((landmark.HasField('visibility') and
                    landmark.visibility < 0.5) or
                    (landmark.HasField('presence') and
                    landmark.presence < 0.5)):
                    continue

                plotted_landmarks[idx] = (-landmark.z, landmark.x, -landmark.y)

            if connections and self.on:
                plot = []
                num_landmarks = len(landmark_list.landmark)
                # Draws the connections if the start and end landmarks are both visible.
                for connection in connections:
                    start_idx = connection[0]
                    end_idx = connection[1]

                    if not (0 <= start_idx < num_landmarks and 0 <= end_idx < num_landmarks):
                        raise ValueError(f'Landmark index is out of range. Invalid connection '
                                        f'from landmark #{start_idx} to landmark #{end_idx}.')
                    
                    if start_idx in plotted_landmarks and end_idx in plotted_landmarks:
                        landmark_pair = [
                            plotted_landmarks[start_idx], plotted_landmarks[end_idx]
                        ]
                        plot.append(ax.plot3D(
                            xs=[landmark_pair[0][0], landmark_pair[1][0]],
                            ys=[landmark_pair[0][1], landmark_pair[1][1]],
                            zs=[landmark_pair[0][2], landmark_pair[1][2]],
                            color='black',
                            linewidth=3)[0])
                        
                current_prediction = self._video_processor.get_current_prediction()

                if current_prediction[0]:
                    text.set_text(current_prediction[0].name)

                else:
                    text.set_text('')
                
                plot.append(text)
                        
            return plot
        

        mp_hands = mp.solutions.hands

        fig = plt.figure(figsize=(3, 3), dpi = 100)
        fm = plt.get_current_fig_manager() 
        fm.window.wm_geometry("+%d+%d" % (0, 0))
        fm.window.attributes("-topmost", True)
        fm.window.attributes("-disabled", True)
        fm.window.attributes("-transparentcolor", "white")
        fm.window.attributes('-alpha', 0)
        fm.window.overrideredirect(True)
        ax = plt.axes(projection='3d', aspect='equal')
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        ax.view_init(elev=10, azim=190)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_zlim3d([-1, 0])
        ax.set_ylim3d([0, 1])
        ax.set_axis_off()
        ax.set_autoscale_on(False)
        text = ax.text(1.5, -1.5, 7, '', transform=ax.transAxes, ha='center', va='bottom', fontdict={'fontsize': 20, 'color': 'green', 'weight': 'bold'})

        ani = animation.FuncAnimation(fig, _update_data, interval=1/60*1000, blit=True)

        plt.show()