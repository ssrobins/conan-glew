from conans import ConanFile, CMake, tools
import os

class Conan(ConanFile):
    name = "glew"
    version = "2.1.0"
    description = "OpenGL extension wrangler library"
    homepage = "https://github.com/nigels-com/glew"
    license = "https://github.com/nigels-com/glew/blob/master/LICENSE.txt"
    url = "https://gitlab.com/ssrobins/conan-" + name
    settings = "os", "compiler", "arch"
    generators = "cmake"
    revision_mode = "scm"
    exports_sources = ["CMakeLists.diff", "CMakeLists.txt"]
    zip_folder_name = "%s-%s" % (name, version)
    zip_name = "%s.tgz" % zip_folder_name
    build_subfolder = "build"
    source_subfolder = "source"

    def system_requirements(self):
        if self.settings.os == "Linux":
            installer = tools.SystemPackageTool()
            installer.install("freeglut3-dev")

    def build_requirements(self):
        self.build_requires.add("cmake_utils/0.3.1#1cf9333e6fba1b7350ec8d4d06f737b54d163eef")

    def source(self):
        tools.download("https://github.com/nigels-com/glew/releases/download/%s/%s" % (self.zip_folder_name, self.zip_name), self.zip_name)
        tools.unzip(self.zip_name)
        os.unlink(self.zip_name)
        os.rename(self.zip_folder_name, self.source_subfolder)

        # Apply a patch to fix error LNK2001: unresolved external symbol _memset
        # when building the shared library on MSVC
        # https://github.com/nigels-com/glew/issues/180:
        tools.patch(base_path=self.source_subfolder, patch_file="CMakeLists.diff")

    def build(self):
        from cmake_utils import cmake_init, cmake_build_debug_release
        cmake = cmake_init(self.settings, CMake(self), self.build_folder)
        cmake_build_debug_release(cmake, self.build_subfolder, self.run)

    def package(self):
        from cmake_utils import cmake_init, cmake_install_debug_release
        cmake = cmake_init(self.settings, CMake(self), self.build_folder)
        cmake_install_debug_release(cmake, self.build_subfolder) 
        if self.settings.compiler == "Visual Studio":
            self.copy("*.pdb", dst="lib", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.debug.libs = ["libglew32d"]
            self.cpp_info.release.libs = ["libglew32"]
            self.cpp_info.libs.append("OpenGL32")
            self.cpp_info.defines.append("GLEW_STATIC")
        elif self.settings.os == "Macos":
            self.cpp_info.debug.libs = ["GLEWd"]
            self.cpp_info.release.libs = ["GLEW"]
            self.cpp_info.exelinkflags.append("-framework OpenGL")
        else:
            self.cpp_info.debug.libs = ["GLEWd"]
            self.cpp_info.release.libs = ["GLEW"]
            self.cpp_info.libs.append("GL")
