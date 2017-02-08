

#import "ViewControllerBase.h"

@interface ViewControllerBase ()

@end

@implementation ViewControllerBase

- (void)viewDidLoad {
    [super viewDidLoad];



{{[]}}

    /*
    self.view.backgroundColor = [UIColor colorWithRed:1 green:1 blue:1 alpha:1];
    //self.view.backgroundColor = [UIColor colorWithRed:0xea/255.0 green:0xea/255.0 blue:0xea/255.0 alpha:1];
    self.view1 = [[UIView alloc] initWithFrame:CGRectMake(10, 10, 200, 100)];
    self.view1.backgroundColor = [UIColor greenColor];
    [self.view addSubview:self.view1];
    self.view2 = [[UIView alloc] initWithFrame:CGRectMake(50, 50, 100, 100)];
    self.view2.backgroundColor = [UIColor redColor];
    [self.view addSubview:self.view2];
    self.label1 = [[UILabel alloc] initWithFrame:CGRectMake(10, 10, 200, 20)];
    self.label1.text = @"Hello world!";
    [self.label1 sizeToFit];
    [self.view addSubview:self.label1];

    */
    
    self.button1 = [[UIButton alloc] initWithFrame:CGRectMake(100, 200, 40, 40)];
    self.button1.backgroundColor = [UIColor yellowColor];
    [self.view addSubview:self.button1];



}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}


@end
