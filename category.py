from tkinter import *
def category_form(window):
    global back_image,logo
    category_frame = Frame(window, width=1165, height=567, bg='white')
    category_frame.place(x=200, y=100)

    heading_label = Label(category_frame, text='مدیریت دسته بندی محصولات', font=('fonts/Persian-Yekan.ttf', 18, 'bold'),
                          bg='#00198f', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    back_image = PhotoImage(file='images/back_button.png')

    back_button = Button(category_frame, image=back_image, bd=0, cursor='hand2', bg='white',
                         command=lambda: category_frame.place_forget())
    back_button.place(x=10, y=45)

    logo=PhotoImage(file='images/category_product.png')
    label=Label(category_frame,image=logo,bg='white')
    label.place(x=30,y=100)



    