from SQLConnect import connect, connect2

cursor = None
def reset_everything(cursor):
    cursor.execute('update "Question" set "Question Score" = 0, "Question Proficiency" = 0, "Ease Factor" = 2.5, "Last Reviewed Date" = NULL, "Interval" = 0, "Repetition No" = 0, "Last Evaluation Response" = NULL')
def main():
    global cursor
    connection, cursor = connect()
    reset_everything(cursor)




if __name__ == "__main__":
    main()