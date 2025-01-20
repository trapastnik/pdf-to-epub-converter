import gradio as gr
import shutil

def copy_file(file_obj):
    return file_obj.name

iface = gr.Interface(fn=copy_file, inputs="file", outputs="file")
iface.launch()