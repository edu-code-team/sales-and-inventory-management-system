from tkinter import * 

def supplier_form(window):
     global back_image
     supplier_frame = Frame(window, width=1165, height=567, bg='white') 
     supplier_frame.place(x=200, y=100)
     heading_label = Label(supplier_frame, text='مدیریت تامین کنندگان', font=('fonts/Persian-Yekan.ttf', 16, 'bold'),
                          bg='#00198f', fg='white')
     heading_label.place(x=0, y=0, relwidth=1)
     back_image = PhotoImage(file='images/back_button.png')

     back_button = Button(supplier_frame, image=back_image, bd=0, cursor='hand2', bg='white',
                         command=lambda: supplier_frame.place_forget())
     back_button.place(x=10, y=30)