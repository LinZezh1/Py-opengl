import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import QTimer
from OpenGL.GL import *
import numpy as np


class OpenGLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.shaderProgram = None
        self.vao = None

    def initializeGL(self):
        """初始化 OpenGL 的设置和着色器"""
        glClearColor(0.0, 0.0, 0.0, 1.0)  # 设置背景颜色为黑色
        glEnable(GL_DEPTH_TEST)  # 启用深度测试

        # 创建并编译 Shader
        vertex_shader_source = """
        #version 330 core
        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec3 aColor;
        out vec3 ourColor;
        void main()
        {
            gl_Position = vec4(aPos, 1.0);
            ourColor = aColor;
        }
        """

        fragment_shader_source = """
        #version 330 core
        in vec3 ourColor;
        out vec4 FragColor;
        void main()
        {
            FragColor = vec4(ourColor, 1.0);
        }
        """

        # 编译着色器
        self.shaderProgram = self.createShaderProgram(vertex_shader_source, fragment_shader_source)

        # 定义三角形的顶点和颜色
        vertices = np.array([
            # 位置           # 颜色
            0.0,  1.0,  0.0,  1.0, 0.0, 0.0,  # 顶点1 (红色)
           -1.0, -1.0,  0.0,  0.0, 1.0, 0.0,  # 顶点2 (绿色)
            1.0, -1.0,  0.0,  0.0, 0.0, 1.0   # 顶点3 (蓝色)
        ], dtype=np.float32)

        # 创建 VAO 和 VBO
        self.vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # 设置顶点属性
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(0))  # 位置属性
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(12))  # 颜色属性
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def createShaderProgram(self, vertex_source, fragment_source):
        """创建、编译并链接着色器程序"""
        vertexShader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertexShader, vertex_source)
        glCompileShader(vertexShader)

        if not glGetShaderiv(vertexShader, GL_COMPILE_STATUS):
            raise RuntimeError(glGetShaderInfoLog(vertexShader))

        fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragmentShader, fragment_source)
        glCompileShader(fragmentShader)

        if not glGetShaderiv(fragmentShader, GL_COMPILE_STATUS):
            raise RuntimeError(glGetShaderInfoLog(fragmentShader))

        shaderProgram = glCreateProgram()
        glAttachShader(shaderProgram, vertexShader)
        glAttachShader(shaderProgram, fragmentShader)
        glLinkProgram(shaderProgram)

        if not glGetProgramiv(shaderProgram, GL_LINK_STATUS):
            raise RuntimeError(glGetProgramInfoLog(shaderProgram))

        glDeleteShader(vertexShader)
        glDeleteShader(fragmentShader)

        return shaderProgram

    def resizeGL(self, w, h):
        """调整视口大小"""
        glViewport(0, 0, w, h)

    def paintGL(self):
        """渲染 OpenGL 内容"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 使用自定义 Shader
        glUseProgram(self.shaderProgram)
        glBindVertexArray(self.vao)

        # 绘制三角形
        glDrawArrays(GL_TRIANGLES, 0, 3)

        glBindVertexArray(0)
        glUseProgram(0)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 OpenGL Shader Example")
        self.setGeometry(100, 100, 800, 600)

        # 创建 OpenGL 小部件并将其设置为主窗口的中央小部件
        self.opengl_widget = OpenGLWidget()
        self.setCentralWidget(self.opengl_widget)

        # 添加一个计时器来触发更新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.opengl_widget.update)
        self.timer.start(16)  # 大约每秒 60 帧


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
