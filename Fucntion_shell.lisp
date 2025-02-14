(ql:quickload 'inferior-shell)

(defvar *load-pathname-directory* (pathname-directory *load-pathname*))
(setf *load-pathname-directory* (rest *load-pathname-directory*))
(defvar *load-pathname-directory-string* (format nil "~{~a/~}" *load-pathname-directory*))
(defvar *python-address* (format nil "C:/~aVisiTor.py" *load-pathname-directory-string*))
(defvar *directory* (format nil "C:/~aAmirPatterns" *load-pathname-directory-string*))
(defvar *clicking-occurred* nil)

(defun run-shell-command (command &optional arglist)
  (let ((shell-request-list
         (append '("C:\\Users\\ambkh\\anaconda3\\python.exe") (list *python-address*)
                 (list command) '("--Dir") (list *directory*) '("--arg2") arglist)))
    (print shell-request-list)
    (inferior-shell:run/ss shell-request-list)))

(defun run-visitor (function &optional dir arg2)
  "Run VisiTor command through shell."
  (run-shell-command function arg2))

(defun click ()
  (run-visitor "click")
  (setf *clicking-occurred* T))

(defun keypress (key)
  (run-visitor "Keypress" nil (list key)))

(defun whatisonscreen (modules)
  (run-visitor "whatisonscreen" *directory* modules))

(defun movecursorto (x y)
  (run-visitor "movecursorto" nil (list x y)))

(defun getmouselocation ()
  (run-visitor "getMouseLocation"))

(defun whereis (filename)
  (run-visitor "whereis" *directory* (list filename)))

(defun continuouspresskey (key)
  (run-visitor "continuouspresskey" nil (list key)))

(defun movecursortopattern (filename)
  (run-visitor "movecursortopattern" *directory* (list filename)))

(defun check-excel-cell-format (x)
  "Check if the input x matches the Excel cell format (a letter followed by a number)."
  (let ((input-string (string x)))
    (and (stringp input-string)
         (> (length input-string) 1)
         (char>= (elt input-string 0) #\A)
         (char<= (elt input-string 0) #\Z)
         (some #'digit-char-p (subseq input-string 1)))))

(defun breakdown-cell (cell)
  "Break down an Excel cell reference into its letter and number parts.
   Returns a list of the form (LETTER NUMBER)."
  (let* ((input-string (string cell))
         (letter (subseq input-string 0 1))
         (number (subseq input-string 1)))
    (list letter number)))

(defun what-is-on-screen (l)
  (let ((on-screen (whatisonscreen l)))
    (act-r-output "what is on screen function ~A!!!" on-screen)
    on-screen))

(defun set-pattern (p)
  (setf *pattern-global* p)
  (act-r-output " Now we have ~s !!!!" *pattern-global*))

(defun move-attention-output-creator (x)
  (format nil "moving attention to ~A" x))

(defun respond-to-move-cursor (z)
  (act-r-output "move-cursor to ~A!!!" z)
  (movecursortopattern z))

(defun respond-to-where-is (z)
  (act-r-output "move-cursor to ~A!!!" z)
  (whereis z))

(defun respond-to-key-press (k)
  (keypress k)
  (when (equal k '("enter"))
    (update-model-click)))

(defun check-string (x)
  (if (and (char-alpha-p (char x 0))
           (every #'digit-char-p (subseq x 1)))
      "cell"
      "text"))

(defun type-check ()
  "true")

(defun respond-to-click-mouse (x y z)
  (click)
  (setf *clicking-occurred* T))

(defun get-key (l sublist)
  "Finds a key given the pair of values associated with it"
  (car (find-if (lambda (parts) (equal sublist (cadr parts))) l)))

(defun concatenate-strings (num1)
  (concatenate 'string "task" (write-to-string num1)))

(defun concatenate-strings-subtask (num1 num2)
  (concatenate 'string
               "subtask"
               (write-to-string num1)
               "_"
               (write-to-string num2)
               "_list"))

(defun get-element-from-list (num1 num2 which)
  (let ((desired_string (concatenate-strings-subtask num1 num2)))
    (case which
      (1 (car (read-from-string (concat "(" desired_string ")"))))
      (2 (cadr (read-from-string (concat "(" desired_string ")"))))
      (t nil))))

(defun get-chars-after-sequence-ci (char1 char2 char3 string)
  (let* ((seq (concatenate 'string char1 char2 char3))
         (pos (search seq string :test #'string-equal)))
    (if pos
        (let ((len (length string)))
          (list (if (< (+ pos (length seq)) len) (string (char string (+ pos (length seq)))) nil)
                (if (< (+ pos (length seq) 1) len) (string (char string (+ pos (length seq) 1))) nil)
                (if (< (+ pos (length seq) 2) len) (string (char string (+ pos (length seq) 2))) nil)))
        nil)))

(defun replace-at-positions (lst vi txt)
  (let ((counter 0))
    (mapcar (lambda (x)
              (incf counter)
              (cond
               ((= counter 15) vi)
               ((= counter 19) txt)
               (t x)))
            lst)))

(defun clicking-occurred? (x)
  *clicking-occurred*)