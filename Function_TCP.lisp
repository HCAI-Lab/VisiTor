(ql:quickload '(:usocket :cl-json))

(defparameter *host* "127.0.0.1")
(defparameter *port* 65432)
(defvar *clicking-occurred* nil)
(defvar *pattern-global* nil)

(defvar *load-pathname-directory* (pathname-directory *load-pathname*))
(setf *load-pathname-directory* (rest *load-pathname-directory*))
(defvar *load-pathname-directory-string* (format nil "~{~a/~}" *load-pathname-directory*))
(defvar *directory* (format nil "C:/~aAmirPatterns" *load-pathname-directory-string*))

(defun send-command (command &rest args)
  "Send a command to the VisiTor TCP server and return the response."
  (let ((socket (usocket:socket-connect *host* *port* :element-type 'character)))
    (unwind-protect
         (progn
           (let ((stream (usocket:socket-stream socket)))
             (let ((json-command (json:encode-json-to-string
                                   `(("function" . ,command)
                                     ("args" . ,args)))))
               (format stream "~A~%" json-command)
               (force-output stream)
               (let ((response (read-line stream)))
                 (json:decode-json-from-string response)))))
      (usocket:socket-close socket))))

(defun click ()
  (send-command "click")
  (setf *clicking-occurred* T))

(defun keypress (key)
  (send-command "keypress" key))

(defun whereis (path)
  (send-command "whereis" path))

(defun find-file (address filename)
  (send-command "find_file" address filename))

(defun addressfinder ()
  (send-command "addressfinder"))

(defun naturalmove (x y)
  (send-command "naturalmove" x y))

(defun getmouselocation ()
  (send-command "getMouseLocation"))

(defun deep-pattern-matching (path template-path)
  (send-command "deep_pattern_matching" path template-path))

(defun whatisonscreen (modules)
  (send-command "whatisonscreen" *directory* modules))

(defun movecursortopattern (filename)
  (send-command "movecursortopattern" *directory* filename))

(defun continuouspresskey (key)
  (send-command "continuouspresskey" key))

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

;; Example usage:
;; (click)
;; (keypress "a")
;; (what-is-on-screen '("module1" "module2"))
;; (naturalmove 100 200)
;; (getmouselocation)
;; (whereis "/path/to/file")
;; (continuouspresskey "b")
;; (movecursortopattern "pattern_file")
;; (deep-pattern-matching "/path/to/source.png" "/path/to/template.png")