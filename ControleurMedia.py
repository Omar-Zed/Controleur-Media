import asyncio
import tkinter as tk
from tkinter import ttk
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

class MediaControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Control")

        self.session_list = []
        self.current_session = None

        self.create_widgets()

        # Lancer la récupération des sessions
        self.root.after(100, self.update_sessions)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Zone d'affichage des informations
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Now Playing", padding="10")
        self.info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.cover_art_label = ttk.Label(self.info_frame)
        self.cover_art_label.grid(row=0, column=0, rowspan=3)

        self.title_label = ttk.Label(self.info_frame, text="Title: ", wraplength=300)
        self.title_label.grid(row=0, column=1, sticky=(tk.W))

        self.artist_label = ttk.Label(self.info_frame, text="Artist: ", wraplength=300)
        self.artist_label.grid(row=1, column=1, sticky=(tk.W))

        # Boutons de contrôle
        self.control_frame = ttk.Frame(self.info_frame, padding="10")
        self.control_frame.grid(row=2, column=1, sticky=(tk.W))

        self.play_button = ttk.Button(self.control_frame, text="Play/Pause", command=self.play_pause)
        self.play_button.grid(row=0, column=0)

        self.next_button = ttk.Button(self.control_frame, text="Next", command=self.next_track)
        self.next_button.grid(row=0, column=1)

        self.previous_button = ttk.Button(self.control_frame, text="Previous", command=self.previous_track)
        self.previous_button.grid(row=0, column=2)

        # Barre de menu pour les sessions
        self.menu_frame = ttk.LabelFrame(self.main_frame, text="Sessions", padding="10")
        self.menu_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.session_listbox = tk.Listbox(self.menu_frame)
        self.session_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.session_listbox.bind('<<ListboxSelect>>', self.on_session_select)

    async def get_all_media_sessions(self):
        sessions = await MediaManager.request_async()
        session_list = sessions.get_sessions()

        all_sessions_info = []

        for session in session_list:
            info = await session.try_get_media_properties_async()
            info_dict = {attr: getattr(info, attr) for attr in dir(info) if not attr.startswith('_')}
            info_dict['genres'] = list(info_dict['genres'])
            info_dict['source_app_user_model_id'] = session.source_app_user_model_id  # Ajoute l'ID de l'application source
            all_sessions_info.append({
                'session': session,
                'info': info_dict
            })

        return all_sessions_info

    def update_sessions(self):
        asyncio.run(self.fetch_sessions())
        # self.root.after(5000, self.update_sessions)

    async def fetch_sessions(self):
        self.session_list = await self.get_all_media_sessions()
        self.session_listbox.delete(0, tk.END)
        for i, media in enumerate(self.session_list):
            session_info = f"{media['info']['title']} - {media['info']['artist']}"
            self.session_listbox.insert(tk.END, session_info)
        self.root.after_idle(self.update_sessions)

    def on_session_select(self, event):
        selected_index = self.session_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.current_session = self.session_list[index]['session']
            self.update_info_display(self.session_list[index]['info'])

    def update_info_display(self, info):
        self.title_label.config(text=f"Title: {info['title']}")
        self.artist_label.config(text=f"Artist: {info['artist']}")
        # Mettre à jour l'image de couverture si disponible
        # Note: Ajoutez la logique pour afficher l'image de couverture ici si elle est disponible dans info

    def play_pause(self):
        if self.current_session:
            asyncio.run(self.current_session.try_toggle_play_pause_async())

    def next_track(self):
        if self.current_session:
            asyncio.run(self.current_session.try_skip_next_async())

    def previous_track(self):
        if self.current_session:
            asyncio.run(self.current_session.try_skip_previous_async())

if __name__ == '__main__':
    root = tk.Tk()
    app = MediaControlApp(root)
    root.mainloop()
